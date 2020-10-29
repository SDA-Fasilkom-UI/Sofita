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
    assignment_id = models.IntegerField()
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

    # kalau disimpan dalam assignment_id, transfer ke assignment_id_list
    def __str__(self):

        # legacy support saat fieldnya masih assignment_id
        if self.assignment_id is not None:
            if type(self.assignment_id) is int:
                self.assignment_id_list = str(self.assignment_id)
            else: 
                self.assignment_id_list = self.assignment_id
            self.assignment_id = None

        if self.status != self.DONE:
            return self.assignment_id_list + " - " + self.get_status_display()

        localtime = timezone.localtime(self.time_created)
        return self.assignment_id_list + " - " + localtime.strftime("%d-%m-%Y %H:%M:%S")

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
