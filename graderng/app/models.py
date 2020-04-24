import hashlib
import secrets

from djongo import models


def generate_token():
    secure_string = secrets.token_urlsafe(69)
    return hashlib.sha256(secure_string.encode()).hexdigest()


class Token(models.Model):
    _id = models.ObjectIdField()

    token = models.CharField(max_length=64, default=generate_token)
    service = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return "{} - {}".format(self.token, self.service)
