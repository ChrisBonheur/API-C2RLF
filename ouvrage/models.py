from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)

class Ouvrage(models.Model):
    title = models.CharField(max_length=255)
    author = models.ManyToManyField(User, related_name='ouvrages')
    year_parution = models.CharField(max_length=4, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    presentation = models.TextField()
    cover_image = models.ImageField(upload_to='ouvrage/cover', null=True, blank=True)
    pdf_file = models.FileField(upload_to='ouvrage/pdf')
    version = models.CharField(max_length=10, null=True, blank=True)
    edition = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)