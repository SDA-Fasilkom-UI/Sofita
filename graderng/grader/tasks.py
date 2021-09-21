import random
import traceback

from celery import group, shared_task
from celery.result import allow_join_result
from django.conf import settings
from django.db.models import Max

from app.constants import K_REDIS_HIGH_PRIORITY
from app.proxy_requests import ProxyRequests
from grader.constants import (
    COMPILATION_ERROR,
    DIRECTORY_NOT_FOUND_OR_INVALID_ERROR,
    DIRECTORY_NOT_FOUND_OR_INVALID_ERROR_TEXT,
    INTERNAL_ERROR,
    SUBMISSION_SKIPPED,
    SUBMISSION_NOT_FOUND,
    VERDICT_FEEDBACK,
)
from grader import cache
from grader.models import Submission
from grader.runner import JavaRunner
from grader.utils import (
    InputOutputNotFoundException,
    compress_gzip_file,
    decompress_gzip_file,
    get_tc_path,
    render_html,
    verdict_to_text,
)


def save_sub(sub, status, verdict, grade):
    sub.status = status
    sub.verdict = verdict
    sub.grade = grade
    sub.save()


@shared_task(acks_late=True)
def grade_submission(submission_id, assignment_id, course_id, activity_id, user_id, attempt_number):
    sub = Submission.objects.filter(id=submission_id).first()
    if sub is None:
        send_feedback.delay(
            assignment_id, course_id, activity_id, user_id, attempt_number,
            SUBMISSION_NOT_FOUND, 0
        )
        return "FAIL (SUBMISSION_NOT_FOUND)"

    sub.status = Submission.GRADING
    sub.save()

    cases_path, num_tc = JavaRunner.validate_and_get_cases_path(
        sub.problem_name)
    if cases_path is None:
        save_sub(sub, Submission.DONE,
                 DIRECTORY_NOT_FOUND_OR_INVALID_ERROR_TEXT, 0)

        send_feedback.delay(
            assignment_id, course_id, activity_id, user_id, attempt_number,
            DIRECTORY_NOT_FOUND_OR_INVALID_ERROR, 0
        )
        return "FAIL (DIRECTORY_NOT_FOUND_OR_INVALID)"

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

    tc_verdict = {}

    curr_tc = list(range(num_tc))
    failed_tc = []
    retry_cnt = {}
    while(len(curr_tc) > 0):
        tasks = []
        for tc in curr_tc:
            cache_manager = cache.RedisCacheManager(
                sub.problem_name, tc, cases_path)

            if not cache_manager.exists():
                in_path, out_path = get_tc_path(cases_path, tc)
                in_gzip = compress_gzip_file(in_path)
                out_gzip = compress_gzip_file(out_path)

                cache_manager.insert(in_gzip, out_gzip)

            tasks.append(grade_testcase.signature((
                exec_content, exec_name, sub.time_limit, sub.memory_limit,
                sub.problem_name, tc
            )))

        tasks_group = group(tasks)
        tasks_result = tasks_group.apply_async()

        # allow waiting task inside task
        with allow_join_result():
            result = tasks_result.get(propagate=False)

        for i, res in enumerate(result):
            tc = curr_tc[i]
            if isinstance(res, Exception):
                retry_cnt[tc] = retry_cnt.get(tc, 0) + 1
                if retry_cnt[tc] <= 5:
                    failed_tc.append(tc)
                else:
                    try:
                        raise res
                    except:
                        tb = traceback.format_exc(10)

                    save_sub(sub, Submission.ERROR, tb, 0)
                    send_feedback.delay(
                        assignment_id, course_id, activity_id, user_id, attempt_number,
                        INTERNAL_ERROR, 0
                    )
                    return "FAIL (RETRY EXCEEDED)"

            else:
                tc_verdict[tc] = res

        curr_tc = failed_tc
        failed_tc = []

    verdict = []
    for i in range(num_tc):
        verdict.append(tc_verdict[i])

    verdict_text = verdict_to_text(verdict)

    num_ac = len([x for x in verdict if x[0] == "AC"])
    grade = num_ac * 100 / len(verdict)

    save_sub(sub, Submission.DONE, verdict_text, grade)

    feedback = render_html(VERDICT_FEEDBACK, {
        "grade": grade,
        "verdict": verdict
    })
    send_feedback.delay(
        assignment_id, course_id, activity_id, user_id, attempt_number,
        feedback, grade
    )
    return "OK"


@shared_task(acks_late=True)
def grade_testcase(exec_content, exec_name, time_limit, memory_limit, problem_name, tc):
    redis_cache = cache.RedisCacheManager(problem_name, tc)

    r_time = redis_cache.get_time_content()
    if not all(r_time):
        raise InputOutputNotFoundException(
            "Input output time not found in redis")

    if settings.DISK_CACHE_ENABLE:
        disk_cache = cache.DiskCacheManager(problem_name, tc)

        d_time = disk_cache.get_time_content()
        if not all(d_time) or d_time[0] < r_time[0] or d_time[1] < r_time[1]:
            r_gzip = redis_cache.get_content()
            if not all(r_gzip):
                raise InputOutputNotFoundException(
                    "Input output not found in redis")

            disk_cache.insert(*r_time, *r_gzip)

        in_gzip, out_gzip = disk_cache.get_content()

    else:
        in_gzip, out_gzip = redis_cache.get_content()

    if (in_gzip is None) or (out_gzip is None):
        raise InputOutputNotFoundException("Input output not found")

    input_text = decompress_gzip_file(in_gzip)
    output_text = decompress_gzip_file(out_gzip)

    return JavaRunner.run(
        exec_content,
        exec_name,
        time_limit,
        memory_limit,
        input_text,
        output_text
    )


@shared_task(priority=K_REDIS_HIGH_PRIORITY)
def skip(assignment_id, course_id, activity_id, user_id, attempt_number):
    send_feedback.delay(
        assignment_id, course_id, activity_id, user_id, attempt_number,
        SUBMISSION_SKIPPED, 0
    )
    return "OK"


@shared_task(bind=True, max_retries=10)
def send_feedback(self, assignment_id, course_id, activity_id, user_id, attempt_number, feedback, grade):
    url = settings.SCELE_URL
    base_params = {
        "wstoken": settings.SCELE_TOKEN,
        "moodlewsrestformat": "json"
    }

    subs = Submission.objects.filter(
        assignment_id=assignment_id,
        user_id=user_id
    )
    if len(subs) > 0:
        max_grade = subs.aggregate(Max("grade"))["grade__max"]
    else:
        max_grade = 0

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
