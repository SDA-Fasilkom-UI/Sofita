#!/bin/bash

if [ "$1" == "worker" ]; then
    celery -A graderng worker -l info --concurrency=$WORKER_CONCURRENCY -O fair --prefetch-multiplier 1
elif [ "$1" == "testcase" ]; then
    celery -A graderng worker -l info -Q testcase --concurrency=$TESTCASE_CONCURRENCY -O fair --prefetch-multiplier 1
elif [ "$1" == "misc" ]; then
    celery -A graderng worker -l info -Q misc --concurrency=$MISC_CONCURRENCY --pool gevent
else
    python3 manage.py collectstatic --noinput
    python3 manage.py migrate
    gunicorn graderng.wsgi --worker-class gevent --bind 0.0.0.0:8080 --log-level info
fi
