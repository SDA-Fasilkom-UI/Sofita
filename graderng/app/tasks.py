import os

import requests
import redis

from celery import shared_task
from django.conf import settings
from django.db.models import Max
from filebrowser.sites import site

from app.models import Submission
from app.sandbox import JavaSandbox, get_redis_box_id


URL = settings.SCELE_URL
PARAMS = {
    "wstoken": settings.SCELE_TOKEN,
    "wsfunction": "mod_assign_save_grade",
    "moodlewsrestformat": "json"
}


@shared_task
def grade(submission_id, assignment_id, user_id, attempt_number):
    sub = Submission.objects.filter(id=submission_id).first()
    if sub is None:
        html = "<p><b>Error | Attempt Grade: 0</b></p>"
        html += "<p>Submission is not found on grader, contact assistant</p>"
        max_grade = get_max_grade(assignment_id, user_id)
        data = {
            "assignmentid": assignment_id,
            "userid": user_id,
            "grade": max_grade,
            "attemptnumber": attempt_number - 1,
            "addattempt": 1,
            "workflowstate": "",
            "applytoall": 0,
            "plugindata[assignfeedbackcomments_editor][text]": html,
            "plugindata[assignfeedbackcomments_editor][format]": 0
        }
        r = requests.post(URL, params=PARAMS, data=data)
        return "[Error] Submission is not found", r.status_code, r.text

    grade, feedback = grade_submission(sub)
    sub.grade = grade
    sub.save()

    max_grade = max(get_max_grade(assignment_id, user_id), grade)
    data = {
        "assignmentid": sub.assignment_id,
        "userid": sub.user_id,
        "grade": max_grade,
        "attemptnumber": sub.attempt_number - 1,
        "addattempt": 1,
        "workflowstate": "",
        "applytoall": 0,
        "plugindata[assignfeedbackcomments_editor][text]": feedback,
        "plugindata[assignfeedbackcomments_editor][format]": 0
    }
    r = requests.post(URL, params=PARAMS, data=data)
    return r.status_code, r.text


@shared_task
def skip(assignment_id, user_id, attempt_number):
    max_grade = get_max_grade(assignment_id, user_id)
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


def grade_submission(sub):
    box_id = get_redis_box_id()

    sandbox = JavaSandbox(box_id, sub.time_limit, sub.memory_limit)

    sandbox.init_isolate()
    sandbox.add_file_from_string(sub.content, sub.filename)
    status_code, error = sandbox.compile(sub.filename)

    if status_code != 0:
        sandbox.cleanup_isolate()
        return 0, convert_error(error)

    filename_no_ext, _ = os.path.splitext(sub.filename)

    location = site.storage.location
    directory = site.directory
    problem_name = sub.problem_name
    problem_path = os.path.join(location, directory, problem_name)
    cases_path = os.path.join(problem_path, "cases")

    if os.path.isdir(cases_path):
        sandbox.add_dir(cases_path)

        dirs = os.listdir(cases_path)
        dir_len = len(dirs)
        tc_len = dir_len - dir_len // 2

        valid = True
        verdict_list = []
        for i in range(1, tc_len + 1):
            in_file = str(i) + ".in"
            out_file = str(i) + ".out"
            input_ = os.path.join(cases_path, in_file)
            output_ = os.path.join(cases_path, out_file)

            if (in_file not in dirs) or (out_file not in dirs):
                valid = False
                break

            status, time = sandbox.run_testcase(
                filename_no_ext, input_, output_)

            verdict_list.append((status, float(time)))

        if valid:
            score = [x for x in verdict_list if x[0] == "AC"]
            grade = len(score) * 100 / len(verdict_list)
            sandbox.cleanup_isolate()
            return grade, convert_verdict(grade, verdict_list)

        else:
            html = "<p><b>Error | Attempt Grade: 0</b></p>"
            html += "<p>Problem directory is not valid, contact assistant</p>"
            sandbox.cleanup_isolate()
            return 0, html

    else:
        html = "<p><b>Error | Attempt Grade: 0</b></p>"
        html += "<p>Problem directory is not found, contact assistant</p>"
        sandbox.cleanup_isolate()
        return 0, html


def convert_error(error):
    html = "<p><b>Compile Error | Attempt Grade: 0</b></p>"
    html += "<p><b>First 20 Lines Compilation Output:</b></p>"
    html += '<table style="border: 1px solid black"><tr><td><tt>'
    for line in error.split("\n")[: 20]:
        html += "{} <br />".format(line)
    html += "</tt></td></tr></table>"
    return html


def convert_verdict(grade, verdict_list):
    html = "<p><b>Attempt Grade: {:.2f}</b></p>".format(grade)
    html += "<p><b>Summary:</b></p>"
    html += '<table style="border-collapse: collapse">'

    ln = len(verdict_list)
    hf = ln - ln // 2

    for i in range(hf):
        content1 = "{}: {} ({:.3f}s)".format(
            i + 1, verdict_list[i][0], verdict_list[i][1])

        content2 = ""
        if hf + i < ln:
            content2 = "{}: {} ({:.3f}s)".format(
                hf + i + 1, verdict_list[hf+i][0], verdict_list[hf+i][1])

        html += "<tr>"
        html += '<td style="border: 1px solid black; text-align=left; padding: 4px;"><tt>{}</tt></td>'.format(
            content1)
        html += '<td style="border: 1px solid black; text-align=left; padding: 4px;"><tt>{}</tt></td>'.format(
            content2)
        html += "</tr>"

    html += "</table><br />"
    html += "<p><tt>AC : Accepted<br />WA : Wrong Answer<br />RTE: Runtime Error<br />TLE: Time Limit Exceeded<br />XX : Unknown Error</tt></p>"
    return html


def get_max_grade(assignment_id, user_id):
    subs = Submission.objects.filter(
        assignment_id=assignment_id, user_id=user_id)
    return subs.aggregate(Max("grade"))["grade__max"]
