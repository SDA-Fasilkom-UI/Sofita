import os

from djongo import models
from django.utils import timezone


class MossJob(models.Model):
    PENDING = "P"
    RUNNING = "R"
    FAILED = "F"
    DONE = "D"
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (FAILED, 'Failed'),
        (DONE, 'Done'),
    ]

    assignment_id = models.IntegerField()
    time_created = models.DateTimeField()
    template = models.TextField(blank=True)
    log = models.TextField()
    zip_file = models.FileField(upload_to='moss/')
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    class Meta:
        ordering = ["-time_created"]

    def __str__(self):
        if self.status != self.DONE:
            return str(self.assignment_id) + " - " + self.get_status_display()

        localtime = timezone.localtime(self.time_created)
        return str(self.assignment_id) + " - " + localtime.strftime("%d-%m-%Y %H:%M:%S")
