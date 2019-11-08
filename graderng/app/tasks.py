import requests
import redis

from django.conf import settings
from celery import shared_task

from app import redis_connection_pool
from app.models import Submission


URL = settings.SCELE_URL
PARAMS = {
    "wstoken": settings.SCELE_TOKEN,
    "wsfunction": "mod_assign_save_grade",
    "moodlewsrestformat": "json"
}

redis = redis.Redis(connection_pool=redis_connection_pool)


@shared_task
def grade(submission_id, assignment_id, user_id, attempt_number):
    sub = Submission.objects.filter(id=submission_id).first()
    if sub is None:
        error = "Submission is not found on grader"
        comment = "<b>{}, contact assistant</b>".format(error)
        data = {
            "assignmentid": assignment_id,
            "userid": user_id,
            "grade": 0,  # Update to highest
            "attemptnumber": attempt_number - 1,
            "addattempt": 1,
            "workflowstate": "",
            "applytoall": 0,
            "plugindata[assignfeedbackcomments_editor][text]": comment,
            "plugindata[assignfeedbackcomments_editor][format]": 0
        }
        r = requests.post(URL, params=PARAMS, data=data)
        return "[Error] {}".format(error), r.status_code, r.text

    # TODO grading

    data = {
        "assignmentid": sub.assignment_id,
        "userid": sub.user_id,
        "grade": 73,  # TODO get data from grade
        "attemptnumber": sub.attempt_number - 1,
        "addattempt": 1,
        "workflowstate": "",
        "applytoall": 0,
        # TODO change
        "plugindata[assignfeedbackcomments_editor][text]": "<b>Accepted</b>",
        "plugindata[assignfeedbackcomments_editor][format]": 0
    }
    r = requests.post(URL, params=PARAMS, data=data)
    return r.status_code, r.text


@shared_task
def skip(assignment_id, user_id, attempt_number):
    data = {
        "assignmentid": assignment_id,
        "userid": user_id,
        "grade": 0,  # TODO Update to highest
        "attemptnumber": attempt_number - 1,
        "addattempt": 1,
        "workflowstate": "",
        "applytoall": 0,
        "plugindata[assignfeedbackcomments_editor][text]": "<b>Skipped</b>",
        "plugindata[assignfeedbackcomments_editor][format]": 0
    }
    r = requests.post(URL, params=PARAMS, data=data)
    return r.status_code, r.text
