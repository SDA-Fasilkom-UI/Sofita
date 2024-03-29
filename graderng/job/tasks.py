import csv
import datetime
import io
import logging
import traceback

from celery import shared_task
from django.db.models import Max
from django.conf import settings
from django.utils import timezone

from grader.models import Submission
from job.models import MossJob, ReportJob
from job.moss import MossDownloader, MossUploader

logger = logging.getLogger(__name__)


@shared_task(time_limit=30*60)
def check_plagiarism(moss_job_id):
    moss_job = MossJob.objects.filter(id=moss_job_id).first()

    if moss_job is None:
        return "FAIL"

    # remove existing file
    moss_job.zip_file.delete(save=False)
    moss_job.time_created = timezone.now()
    moss_job.log = "Running"
    moss_job.status = MossJob.RUNNING
    moss_job.save()

    uploader = MossUploader(settings.MOSS_USER_ID, "java")
    downloader = MossDownloader()

    assignment_ids = [int(id.strip(' '))
                      for id in moss_job.assignment_id_list.split(',')]

    submissions = Submission.objects.filter(
        assignment_id__in=assignment_ids)

    if not submissions:
        moss_job.log = "Assignment ID is invalid"
        moss_job.status = MossJob.FAILED
        moss_job.save()

        return "FAIL"

    # add template
    if moss_job.template:
        uploader.add_base_file_from_string(
            moss_job.template, "Template.java")

    # filter highest submissions
    highest_submissions = []
    user_ids = set(submissions.values_list("user_id", flat=True))
    for user_id in user_ids:
        user_highest_sub = submissions.filter(
            user_id=user_id).order_by('-grade', '-time_modified').first()
        highest_submissions.append(user_highest_sub)

    for sub in highest_submissions:
        if not sub.id_number:
            display_name = "UserID({})_{}".format(
                sub.user_id, sub.filename)
        else:
            display_name = "{}_{}".format(
                sub.id_number, sub.filename)
        uploader.add_file_from_string(sub.content, display_name)

    try:
        logger.info("Start contacting Moss server.")

        url = uploader.send()
        logger.info("Done uploading Moss job.")

        zip_file = downloader.download_and_zip_report(url)
        logger.info("Done downloading Moss job.")

        # rejoin assignment id for zip file naming
        assignment_ids_str = [str(id) for id in assignment_ids]
        assignment_ids_joined = '-'.join(assignment_ids_str)

        filename = "{}_{}.zip".format(
            assignment_ids_joined, int(moss_job.time_created.timestamp()))

        moss_job.zip_file.save(filename, zip_file, save=False)
        moss_job.log = "Success"
        moss_job.status = MossJob.DONE
        moss_job.save()

        return "OK"
    except:
        tb = traceback.format_exc(10)

        moss_job.log = tb
        moss_job.status = MossJob.FAILED
        moss_job.save()

        return ("FAIL", tb)


@shared_task(time_limit=30*60)
def generate_report(report_job_id):
    report_job = ReportJob.objects.filter(id=report_job_id).first()

    if report_job is None:
        return "FAIL"

    # remove existing file
    report_job.csv_file.delete(save=False)
    report_job.time_created = timezone.now()
    report_job.log = "Running"
    report_job.status = ReportJob.RUNNING
    report_job.save()

    submissions = Submission.objects.filter(
        assignment_id=report_job.assignment_id)

    if not submissions:
        report_job.log = "Assignment ID is invalid"
        report_job.status = ReportJob.FAILED
        report_job.save()

        return "FAIL"

    result = {}
    id_mapping = {}
    max_attempt_number = 0
    for sub in submissions:
        if sub.user_id not in result:
            result[sub.user_id] = {}

        dt = datetime.datetime.fromtimestamp(sub.time_modified)
        dt = timezone.make_aware(dt)
        result[sub.user_id]["{}_grade".format(sub.attempt_number)] = sub.grade
        result[sub.user_id]["{}_time".format(sub.attempt_number)] = \
            dt.strftime("%d-%m-%Y %H:%M:%S")

        if sub.id_number:
            id_mapping[sub.user_id] = sub.id_number

        if sub.attempt_number > max_attempt_number:
            max_attempt_number = sub.attempt_number

    fieldnames = ["student_id"]
    for num in range(max_attempt_number):
        fieldnames.extend(["{}_grade".format(num + 1),
                           "{}_time".format(num + 1)])
    fieldnames.append("max_grade")

    buf = io.StringIO()
    cf = csv.DictWriter(buf, fieldnames=fieldnames)
    cf.writeheader()

    for user_id, data in result.items():
        student_id = id_mapping.get(user_id, "UserID({})".format(user_id))
        max_grade = submissions \
            .filter(user_id=user_id) \
            .aggregate(Max("grade"))["grade__max"]

        data["student_id"] = student_id
        data["max_grade"] = max_grade

        row = {}
        for fieldname in fieldnames:
            row[fieldname] = data.get(fieldname, "-")

        cf.writerow(row)

    filename = "{}_{}.csv".format(
        report_job.assignment_id, int(report_job.time_created.timestamp()))

    report_job.csv_file.save(filename, buf, save=False)
    report_job.log = "Success"
    report_job.status = MossJob.DONE
    report_job.save()

    return "OK"
