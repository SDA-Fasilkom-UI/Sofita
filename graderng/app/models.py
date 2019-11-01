from djongo import models
import hashlib, secrets

def generate_token():
    secure_string = secrets.token_urlsafe(69)
    return hashlib.sha256(secure_string.encode())

# Create your models here.
class Submission(models.Model):
    name = models.CharField(max_length=255)
    problem_name = models.CharField(max_length=255)
    assignment_id = models.IntegerField()
    user_id = models.IntegerField()
    content = models.TextField()
    id_number = models.CharField(max_length=15)
    time_limit = models.IntegerField(default=3)
    memory_limit = models.IntegerField(default=256)

class Token(models.Model):
    token = models.CharField(max_length=63, default=generate_token)
