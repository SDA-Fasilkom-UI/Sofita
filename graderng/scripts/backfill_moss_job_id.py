from job.models import MossJob


def run():
    print("[BACKFILL_MOSS_JOB_ID] Starting...")

    jobs = MossJob.objects.filter(assignment_id_list=None)
    for job in jobs:
        job.assignment_id_list = str(job.assignment_id)
        job.save()

    print("[BACKFILL_MOSS_JOB_ID] Updated {} jobs...".format(len(jobs)))
