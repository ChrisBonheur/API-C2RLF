from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from apiC2rlf.utils import crop_image, edit_height_by_width


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
    price = models.FloatField()
    cover_image_min = models.ImageField(upload_to='ouvrage/cover/min', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.cover_image:
            original_filename = str(self.cover_image)
            min_file_name = 'min_' + original_filename
            self.cover_image_min.save(min_file_name, self.cover_image, save=False)
        super().save(*args, **kwargs)

        if self.cover_image_min and self.cover_image:
            crop_image(self.cover_image_min.path, 600, 400)
            edit_height_by_width(self.cover_image.path, 600)
