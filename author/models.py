from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from os import system
from apiC2rlf.utils import crop_image
from django.contrib.auth.models import User

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author')
    adress = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=30, null=True, blank=True)
    institution = models.CharField(max_length=100)
    aboutAuthor = models.CharField(max_length=255, null=True, blank=True)
    photo = models.ImageField(null=True, blank=True, upload_to="pictures/avatars")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            crop_image(self.photo.path, 400, 400)

@receiver(pre_save, sender=Author)
def post_save_receiver(sender, instance, **kwargs):
    if instance.photo:
        system(f'rm {instance.photo.url}')
    