import os
import pymongo

""" 
This script intended for initiating mongo.
"""

DB_NAME = os.environ.get('MONGO_DBNAME', 'test-mongo')
DB_HOST = os.environ.get('MONGO_HOST', 'localhost')
DB_PORT = os.environ.get('MONGO_PORT', 27017)
DB_USERNAME = os.environ.get('MONGO_USERNAME')
DB_PASSWORD = os.environ.get('MONGO_PASSWORD')


def main():
    if (DB_USERNAME is None) or (DB_PASSWORD is None):
        client = pymongo.MongoClient(
            'mongodb://{}:{}/{}'.format(DB_HOST, DB_PORT, DB_NAME))
    else:
        client = pymongo.MongoClient(
            'mongodb://{}:{}@{}:{}/{}'.format(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME))

    db = client[DB_NAME]

    col_subs = db.grader_submission
    col_subs.create_index([("time_modified", -1), ("_id", -1)])

    col_report_job = db.job_reportjob
    col_report_job.create_index([("time_created", -1), ("_id", -1)])

    col_moss_job = db.job_mossjob
    col_moss_job.create_index([("time_created", -1), ("_id", -1)])


if __name__ == "__main__":
    main()
