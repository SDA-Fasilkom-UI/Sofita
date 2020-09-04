import random
import requests

from celery import shared_task
from django.conf import settings
from django.db.models import Max

from app.constants import K_REDIS_HIGH_PRIORITY
from app.proxy_requests import ProxyRequests
from grader.constants import (
    SUBMISSION_SKIPPED,
    SUBMISSION_NOT_FOUND
)
from grader.models import Submission
from grader.runner import JavaRunner


@shared_task(acks_late=True)
def grade(submission_id, assignment_id, course_id, activity_id, user_id, attempt_number):
    sub = Submission.objects.filter(_id=submission_id).first()

    if sub is None:
        send_feedback.delay(
            assignment_id, course_id, activity_id, user_id, attempt_number,
            SUBMISSION_NOT_FOUND, 0
        )

        return "FAIL"

    sub.status = Submission.GRADING
    sub.save()

    grade, feedback, verdict = JavaRunner(sub).grade_submission()

    sub.status = Submission.DONE
    sub.verdict = verdict
    sub.grade = grade
    sub.save()

    send_feedback.delay(
        assignment_id, course_id, activity_id, user_id, attempt_number,
        feedback, grade
    )

    return "OK"


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
