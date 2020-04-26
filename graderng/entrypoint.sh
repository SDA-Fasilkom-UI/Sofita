#!/bin/bash

if [ "$1" == "celery" ]; then
    celery -A graderng worker -l info --concurrency=$CELERY_CONCURRENCY --pool threads
else
    python3 manage.py collectstatic --noinput
    python3 manage.py migrate
    gunicorn graderng.wsgi --threads 2 --bind 0.0.0.0:18080 --log-level info
fi
