# https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

from graderng.celery import app as celery_app

__all__ = ('celery_app',)
