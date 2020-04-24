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

    _id = models.ObjectIdField()

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

    name = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["-time_created"]

    def __str__(self):
        if self.status != self.DONE:
            return str(self.assignment_id) + " - " + self.get_status_display()

        localtime = timezone.localtime(self.time_created)
        return str(self.assignment_id) + " - " + localtime.strftime("%d-%m-%Y %H:%M:%S")

    @property
    def id_(self):
        """
        Same as _id, but string.
        """
        return str(self._id)
