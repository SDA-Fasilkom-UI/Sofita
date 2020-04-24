import traceback

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from app.constants import K_REDIS_LOW_PRIORITY
from grader.models import Submission
from job.models import MossJob, ReportJob
from job.utils import MossDownloader, MossUploader


@shared_task(soft_time_limit=30*60, priority=K_REDIS_LOW_PRIORITY)
def check_plagiarism(moss_job_id):
    moss_job = MossJob.objects.filter(_id=moss_job_id).first()

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

    submissions = Submission.objects.filter(
        assignment_id=moss_job.assignment_id)

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
            user_id=user_id).order_by('-grade').first()
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
        url = uploader.send()
        zip_file = downloader.download_and_zip_report(url)

        filename = "{}_{}.zip".format(
            moss_job.assignment_id, int(moss_job.time_created.timestamp()))

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


@shared_task(soft_time_limit=30*60, priority=K_REDIS_LOW_PRIORITY)
def generate_report(report_job_id):
    report_job = ReportJob.objects.filter(_id=report_job_id).first()

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

    # TO-DO with submissions
    report_job.log = "Not Implemented"
    report_job.status = ReportJob.FAILED
    report_job.save()
    return "FAIL"
