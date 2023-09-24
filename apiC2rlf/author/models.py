from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from os import system

from django.contrib.auth.models import User

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author')
    adress = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=30, null=True, blank=True)
    institution = models.CharField(max_length=100)
    aboutAuthor = models.CharField(max_length=255, null=True, blank=True)
    photo = models.ImageField(null=True, blank=True, upload_to="pictures/avatars")

@receiver(post_save, sender=Author)
def post_delete_receiver(sender, instance, **kwargs):
    pass