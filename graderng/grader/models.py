import datetime

from djongo import models
from django.utils import timezone


class Submission(models.Model):
    PENDING = "P"
    GRADING = "G"
    DONE = "D"
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (GRADING, 'Grading'),
        (DONE, 'Done'),
    ]

    problem_name = models.CharField(max_length=256)
    filename = models.CharField(max_length=256)
    assignment_id = models.IntegerField()
    course_id = models.IntegerField()
    activity_id = models.IntegerField()
    user_id = models.IntegerField()
    content = models.TextField()
    id_number = models.CharField(max_length=16)
    time_limit = models.IntegerField(default=2)
    memory_limit = models.IntegerField(default=256)
    attempt_number = models.IntegerField()

    due_date = models.IntegerField()
    cut_off_date = models.IntegerField()
    time_modified = models.IntegerField()

    grade = models.IntegerField(default=0)
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    class Meta:
        ordering = ["-time_modified"]

    def __str__(self):
        if not self.id_number:
            return "UserID({}) - {}({})".format(self.user_id, self.problem_name, self.attempt_number)
        return "{} - {}({})".format(self.id_number, self.problem_name, self.attempt_number)

    @property
    def formatted_time_modified(self):
        dt = datetime.datetime.fromtimestamp(self.time_modified)
        return timezone.make_aware(dt)
