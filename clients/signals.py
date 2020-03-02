from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ClientProfile
from .tokens import create_token


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        token = create_token()
        ClientProfile.objects.create(user=instance, registration_token=token)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.clientprofile.save()
