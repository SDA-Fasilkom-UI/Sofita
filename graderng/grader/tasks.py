import os

import random
import requests

from celery import shared_task
from django.conf import settings
from django.db.models import Max

from grader.constants import (
    SUBMISSION_SKIPPED,
    SUBMISSION_NOT_FOUND
)
from grader.models import Submission
from grader.runner import JavaRunner


@shared_task
def grade(submission_id, assignment_id, user_id, attempt_number):
    sub = Submission.objects.filter(id=submission_id).first()

    if sub is None:
        send_feedback.delay(
            assignment_id, user_id, attempt_number,
            SUBMISSION_NOT_FOUND
        )

        return "FAIL"

    sub.status = Submission.GRADING
    sub.save()

    grade, feedback = JavaRunner(sub).grade_submission()

    sub.status = Submission.DONE
    sub.grade = grade
    sub.save()

    send_feedback.delay(assignment_id, user_id, attempt_number, feedback)

    return "OK"


@shared_task
def skip(assignment_id, user_id, attempt_number):
    send_feedback.delay(
        assignment_id,
        user_id,
        attempt_number,
        SUBMISSION_SKIPPED
    )
    return "OK"


@shared_task(bind=True, max_retries=10)
def send_feedback(self, assignment_id, user_id, attempt_number, feedback, add_attempt=True):
    url = settings.SCELE_URL
    params = {
        "wstoken": settings.SCELE_TOKEN,
        "wsfunction": "mod_assign_save_grade",
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

    data = {
        "assignmentid": assignment_id,
        "userid": user_id,
        "grade": max_grade,
        "attemptnumber": attempt_number - 1,
        "addattempt": int(add_attempt),
        "workflowstate": "",
        "applytoall": 0,
        "plugindata[assignfeedbackcomments_editor][text]": feedback,
        "plugindata[assignfeedbackcomments_editor][format]": 1  # HTML
    }

    try:
        if len(os.environ.get("HTTP_PROXY", "")) == 0:
            r = requests.post(url, params=params, data=data)
        else:
            proxies = {
                "http": os.environ.get("HTTP_PROXY"),
                "https": os.environ.get("HTTP_PROXY")
            }
            r = requests.post(url, params=params, data=data, proxies=proxies)
    except Exception as exc:
        rand = random.uniform(2, 4)
        self.retry(exc=exc, countdown=rand ** self.request.retries)

    return (r.status_code, r.text)
