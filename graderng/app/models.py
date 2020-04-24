import hashlib
import secrets

from djongo import models


class BaseModel(models.Model):
    _id = models.ObjectIdField()

    class Meta:
        abstract = True

    @property
    def id_(self):
        """
        Same as _id, but string.
        """
        return str(self._id)


def generate_token():
    secure_string = secrets.token_urlsafe(69)
    return hashlib.sha256(secure_string.encode()).hexdigest()


class Token(BaseModel):
    token = models.CharField(max_length=64, default=generate_token)
    service = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return "{} - {}".format(self.token, self.service)
