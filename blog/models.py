from django.db import models
from django.urls import reverse
from django.utils import timezone

from personnel.models import PersonnelProfile


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT)
    creation_date = models.DateField(default=timezone.now())
    publication_date = models.DateField(default=None, null=True)
    publicized = models.BooleanField(default=False)
    author = models.ForeignKey(PersonnelProfile, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f'{self.author} :  {self.title} | {self.creation_date}'

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
