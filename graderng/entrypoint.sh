#!/bin/bash

if [ "$1" == "celery" ]; then
    celery -A graderng worker
else
    python3 manage.py collectstatic --noinput
    python3 manage.py migrate
    gunicorn graderng.wsgi --workers 3 --bind 0.0.0.0:8080
fi
