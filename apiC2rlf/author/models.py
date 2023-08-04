from django.db import models

from django.contrib.auth.models import User

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author')
    adress = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=30, null=True, blank=True)
    institution = models.CharField(max_length=100)
    aboutAuthor = models.CharField(max_length=255)
    photo = models.ImageField(null=True, blank=True, upload_to="pictures/avatars")