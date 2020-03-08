from djongo import models


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
        if not self.id_number:
            return "UserID({}) - {}({})".format(self.user_id, self.problem_name, self.attempt_number)
        return "{} - {}({})".format(self.id_number, self.problem_name, self.attempt_number)
