from django.db import models
from django.utils import timezone


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    duration = models.IntegerField()

    def __str__(self):
        return self.name


class ContactFormMessage(models.Model):
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=5000)
    sender = models.CharField(max_length=50)
    email = models.EmailField()
    sending_date = models.DateTimeField(default=timezone.now())
    contact_consent = models.BooleanField()

    def __str__(self):
        return f'{self.email}: {self.sending_date}'
