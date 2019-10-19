from celery import shared_task

import time


@shared_task
def do(x, y):
    time.sleep(3)
    return x + y
