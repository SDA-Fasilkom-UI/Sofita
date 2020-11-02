import os
import pymongo


DB_NAME = os.environ.get('MONGO_DBNAME', 'test-mongo')
DB_HOST = os.environ.get('MONGO_HOST', 'localhost')
DB_PORT = os.environ.get('MONGO_PORT', 27017)
DB_USERNAME = os.environ.get('MONGO_USERNAME')
DB_PASSWORD = os.environ.get('MONGO_PASSWORD')


def run():
    print("[INIT_MONGO] Initializing mongo...")
    client = pymongo.MongoClient(
        host=DB_HOST,
        port=int(DB_PORT),
        username=DB_USERNAME,
        password=DB_PASSWORD,
    )
    db = client[DB_NAME]

    k01_grader_job_index(db)

    client.close()

    print("[INIT_MONGO] Done...")


def k01_grader_job_index(db):
    """
    Add index to grader and job
    """
    print("[INIT_MONGO] k01_grader_job_index...")
    col_subs = db.grader_submission
    col_subs.create_index([("time_modified", -1), ("_id", -1)])

    col_report_job = db.job_reportjob
    col_report_job.create_index([("time_created", -1), ("_id", -1)])

    col_moss_job = db.job_mossjob
    col_moss_job.create_index([("time_created", -1), ("_id", -1)])
