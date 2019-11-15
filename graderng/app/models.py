import hashlib
import secrets

from djongo import models


def generate_token():
    secure_string = secrets.token_urlsafe(69)
    return hashlib.sha256(secure_string.encode()).hexdigest()


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
        return "{} - {} - {}".format(self.id_number, self.problem_name, self.attempt_number)


class Token(models.Model):
    token = models.CharField(max_length=64, default=generate_token)
    service = models.CharField(max_length=32)

    def __str__(self):
        return "{} - {}".format(self.token, self.service)
