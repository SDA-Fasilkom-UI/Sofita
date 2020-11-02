import os

from djongo import models
from django.utils import timezone

from app.models import BaseModel


class MossJob(BaseModel):
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
    assignment_id = models.IntegerField(
        help_text="Deprecated. Use assignment_id_list instead.")
    assignment_id_list = models.CharField(max_length=128)
    time_created = models.DateTimeField()
    template = models.TextField(blank=True)
    log = models.TextField()
    zip_file = models.FileField(upload_to='moss/')
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    name = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["-time_created"]

    def __str__(self):
        assignment_ids = self.assignment_id_list
        if assignment_ids is None or len(assignment_ids) == 0:
            assignment_ids = str(self.assignment_id)

        if self.status != self.DONE:
            return assignment_ids + " - " + self.get_status_display()

        localtime = timezone.localtime(self.time_created)
        return assignment_ids + " - " + localtime.strftime("%d-%m-%Y %H:%M:%S")


class ReportJob(BaseModel):
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
    log = models.TextField()
    csv_file = models.FileField(upload_to='reports/')
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    name = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["-time_created"]

    def __str__(self):
        if self.status != self.DONE:
            return str(self.assignment_id) + " - " + self.get_status_display()

        localtime = timezone.localtime(self.time_created)
        return str(self.assignment_id) + " - " + localtime.strftime("%d-%m-%Y %H:%M:%S")
