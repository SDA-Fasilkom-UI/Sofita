import os

import requests

from celery import shared_task
from django.conf import settings
from django.db.models import Max

from app.models import Submission
from app.grader import grade_submission


@shared_task
def grade(submission_id, assignment_id, user_id, attempt_number):
    sub = Submission.objects.filter(id=submission_id).first()

    if sub is None:
        return send_feedback(
            assignment_id, user_id, attempt_number,
            submission_not_found_feedback()
        )

    sub.status = Submission.GRADING
    sub.save()

    grade, feedback = grade_submission(sub)

    sub.status = Submission.DONE
    sub.grade = grade
    sub.save()

    return send_feedback(assignment_id, user_id, attempt_number, feedback)


@shared_task
def skip(assignment_id, user_id, attempt_number):
    return send_feedback(
        assignment_id,
        user_id,
        attempt_number,
        submission_skipped_feedback()
    )


def send_feedback(assignment_id, user_id, attempt_number, feedback, add_attempt=True):
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
    max_grade = subs.aggregate(Max("grade"))["grade__max"]

    data = {
        "assignmentid": assignment_id,
        "userid": user_id,
        "grade": max_grade,
        "attemptnumber": attempt_number - 1,
        "addattempt": int(add_attempt),
        "workflowstate": "",
        "applytoall": 0,
        "plugindata[assignfeedbackcomments_editor][text]": feedback,
        "plugindata[assignfeedbackcomments_editor][format]": 0
    }

    r = requests.post(url, params=params, data=data)
    return r.status_code, r.text


def submission_skipped_feedback():
    html = "<b>Skipped</b>"
    return html


def submission_not_found_feedback():
    html = "<p><b>Error | Attempt Grade: 0</b></p>"
    html += "<p>Submission is not found on grader, contact assistant</p>"
    return html
