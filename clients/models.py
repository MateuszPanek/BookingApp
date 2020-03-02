from PIL import Image
from django.contrib.auth.models import User
from django.db import models


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(default=None, null=True)
    address = models.CharField(max_length=200)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    registration_token = models.CharField(max_length=1000, default=None, null=True)
    confirmed_token = models.CharField(max_length=1000, default=None, null=True)

    def __str__(self):
        return f'Client : {self.user.first_name} {self.user.last_name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class ClientEmailUpdate(models.Model):
    linked_profile = models.OneToOneField(ClientProfile, on_delete=models.CASCADE)
    email = models.EmailField(null=True, default=None)

    def __str__(self):
        return f'Update Email for {self.linked_profile.user.username}'
