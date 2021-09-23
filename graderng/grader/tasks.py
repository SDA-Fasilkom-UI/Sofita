import random

from celery import chord, shared_task
from django.conf import settings
from django.db.models import Max

from app.constants import K_REDIS_HIGH_PRIORITY
from app.proxy_requests import ProxyRequests
from grader.constants import (
    ACCEPTED,
    COMPILATION_ERROR,
    DIRECTORY_NOT_FOUND_OR_INVALID_ERROR,
    DIRECTORY_NOT_FOUND_OR_INVALID_ERROR_TEXT,
    INTERNAL_ERROR,
    SUBMISSION_SKIPPED,
    SUBMISSION_NOT_FOUND,
    VERDICT_FEEDBACK,
)
from grader.cache import TestcaseCache
from grader.models import Submission
from grader.runner import JavaRunner
from grader.utils import (
    compress_gzip_file,
    decompress_gzip_file,
    get_num_tc,
    get_tc_mtime,
    get_tc_path,
    render_html,
    validate_cases_path,
    verdict_to_text,
)


def save_sub(sub, status, verdict, grade):
    sub.status = status
    sub.verdict = verdict
    sub.grade = grade
    sub.save()


def save_sub_with_id(sub_id, status, verdict, grade):
    Submission.objects.filter(id=sub_id).update(
        status=status, verdict=verdict, grade=grade)


@shared_task(acks_late=True)
def grade_submission(submission_id, assignment_id, course_id, activity_id, user_id, attempt_number):

    # check if submission exists
    sub = Submission.objects.filter(id=submission_id).first()
    if sub is None:
        send_feedback.delay(
            assignment_id, course_id, activity_id, user_id, attempt_number,
            SUBMISSION_NOT_FOUND, 0
        )
        return "FAIL (SUBMISSION_NOT_FOUND)"

    sub.status = Submission.COMPILING
    sub.save()

    # validate cases directory
    is_valid = validate_cases_path(sub.problem_name)
    if not is_valid:
        save_sub(sub, Submission.DONE,
                 DIRECTORY_NOT_FOUND_OR_INVALID_ERROR_TEXT, 0)

        send_feedback.delay(
            assignment_id, course_id, activity_id, user_id, attempt_number,
            DIRECTORY_NOT_FOUND_OR_INVALID_ERROR, 0
        )
        return "FAIL (DIRECTORY_NOT_FOUND_OR_INVALID)"

    num_tc = get_num_tc(sub.problem_name)

    # compile
    compile_code, error, exec_name, exec_content = JavaRunner.compile(
        sub.content,
        sub.filename
    )
    if compile_code != 0:
        error_minimum = "\n".join(error.split("\n")[:20])

        save_sub(sub, Submission.DONE, error_minimum, 0)

        feedback = render_html(
            COMPILATION_ERROR, {"error": error_minimum})
        send_feedback.delay(
            assignment_id, course_id, activity_id, user_id, attempt_number,
            feedback, 0
        )
        return "OK (COMPILE_ERROR)"

    # grade each testcase
    tasks = []
    for i in range(1, num_tc+1):
        cache_mtime = TestcaseCache.get_mtime(sub.problem_name, i)
        actual_mtime = get_tc_mtime(sub.problem_name, i)

        if actual_mtime > cache_mtime:
            in_path, out_path = get_tc_path(sub.problem_name, i)
            in_gzip = compress_gzip_file(in_path)
            out_gzip = compress_gzip_file(out_path)

            TestcaseCache.insert(sub.problem_name, i,
                                 in_gzip, out_gzip, actual_mtime)
        else:
            in_gzip, out_gzip = TestcaseCache.get_content(
                sub.problem_name, i)

        tasks.append(grade_testcase.signature((
            exec_content, exec_name, sub.time_limit, sub.memory_limit,
            in_gzip, out_gzip, i,
        )))

    sub_identifier = {
        "submission_id": submission_id,
        "assignment_id": assignment_id,
        "course_id": course_id,
        "activity_id": activity_id,
        "user_id": user_id,
        "attempt_number": attempt_number,
    }
    c = chord(tasks, grade_success_handler.s(sub_identifier).on_error(
        forward_fail_handler.s(sub_identifier)))
    c.apply_async()

    sub.status = Submission.GRADING
    sub.save()
    return "OK"


@shared_task(bind=True, acks_late=True, max_retries=5)
def grade_testcase(self, exec_content, exec_name, time_limit, memory_limit,
                   in_gzip, out_gzip, tc_num):

    input_text = decompress_gzip_file(in_gzip)
    output_text = decompress_gzip_file(out_gzip)

    try:
        result = JavaRunner.run(
            exec_content,
            exec_name,
            time_limit,
            memory_limit,
            input_text,
            output_text
        )
        return tc_num, result
    except Exception as exc:
        rand = random.uniform(2, 4)
        self.retry(exc=exc, countdown=rand ** self.request.retries)


@shared_task(acks_late=True)
def grade_success_handler(results, sub_identifier):
    verdict = [None]*len(results)
    for tc_num, tc_result in results:
        verdict[tc_num-1] = tc_result

    num_ac = len([x for x in verdict if x[0] == ACCEPTED])
    grade = num_ac * 100 / len(verdict)

    verdict_text = verdict_to_text(verdict)
    save_sub_with_id(
        sub_identifier["submission_id"], Submission.DONE, verdict_text, grade)

    feedback = render_html(VERDICT_FEEDBACK, {
        "grade": grade,
        "verdict": verdict
    })
    send_feedback.delay(
        sub_identifier["assignment_id"],
        sub_identifier["course_id"],
        sub_identifier["activity_id"],
        sub_identifier["user_id"],
        sub_identifier["attempt_number"],
        feedback, grade
    )
    return "OK"


@shared_task(acks_late=True)
def grade_fail_handler(req, exc, tb, sub_identifier):
    msg = "Error due to `{}`. Please check logs.".format(str(exc))
    save_sub_with_id(sub_identifier["submission_id"], Submission.ERROR, msg, 0)
    send_feedback.delay(
        sub_identifier["assignment_id"],
        sub_identifier["course_id"],
        sub_identifier["activity_id"],
        sub_identifier["user_id"],
        sub_identifier["attempt_number"],
        INTERNAL_ERROR, 0
    )
    return "OK"


@shared_task(acks_late=True)
def forward_fail_handler(req, exc, tb, sub_identifier):
    """
    If grading fail, it will raise exception at the current worker. In case
    fail happens at `testcase` workers, we cannot change the submission from
    it because the worker is designed not to connect to database. This function
    will forward the error as event to main worker.
    """
    grade_fail_handler.delay(req, exc, tb, sub_identifier)


@shared_task(priority=K_REDIS_HIGH_PRIORITY)
def skip(assignment_id, course_id, activity_id, user_id, attempt_number):
    send_feedback.delay(
        assignment_id, course_id, activity_id, user_id, attempt_number,
        SUBMISSION_SKIPPED, 0
    )
    return "OK"


@shared_task(bind=True, acks_late=True, max_retries=10)
def send_feedback(self, assignment_id, course_id, activity_id,
                  user_id, attempt_number, feedback, grade):

    url = settings.SCELE_URL
    base_params = {
        "wstoken": settings.SCELE_TOKEN,
        "moodlewsrestformat": "json"
    }

    subs = Submission.objects.filter(
        assignment_id=assignment_id,
        user_id=user_id
    )

    max_grade = 0
    if len(subs) > 0:
        max_grade = subs.aggregate(Max("grade"))["grade__max"]

    feedback_data = {
        "assignmentid": assignment_id,
        "userid": user_id,
        "grade": grade,
        "attemptnumber": attempt_number - 1,
        "addattempt": 1,
        "workflowstate": "",
        "applytoall": 0,
        "plugindata[assignfeedbackcomments_editor][text]": feedback,
        "plugindata[assignfeedbackcomments_editor][format]": 1  # HTML
    }

    max_grade_data = {
        "source": "assignment",
        "component": "mod_assign",
        "itemnumber": 0,
        "courseid": course_id,
        "activityid": activity_id,
        "grades[0][studentid]": user_id,
        "grades[0][grade]": max_grade
    }

    try:
        p = ProxyRequests.post(
            url,
            params={**base_params, "wsfunction": "mod_assign_save_grade"},
            data=feedback_data
        )
        q = ProxyRequests.post(
            url,
            params={**base_params, "wsfunction": "core_grades_update_grades"},
            data=max_grade_data
        )
    except Exception as exc:
        rand = random.uniform(2, 4)
        self.retry(exc=exc, countdown=rand ** self.request.retries)

    return (p.status_code, p.text, q.status_code, q.text)
