#!/bin/bash

if [ "$1" == "worker" ]; then
    celery -A graderng worker -l info --concurrency=$WORKER_CONCURRENCY
elif [ "$1" == "testcases" ]; then
    celery -A graderng worker -l warn -Q testcases --concurrency=$TESTCASES_CONCURRENCY
elif [ "$1" == "feedbacks_jobs" ]; then
    celery -A graderng worker -l info -Q feedbacks_jobs --concurrency=$FEEDBACKS_JOBS_CONCURRENCY --pool gevent
else
    python3 manage.py collectstatic --noinput
    python3 manage.py migrate
    gunicorn graderng.wsgi --worker-clas gevent --bind 0.0.0.0:8080 --log-level info --log-file -
fi
