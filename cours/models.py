from django.db import models
from django.contrib.auth.models import User

from apiC2rlf.utils import crop_image, edit_height_by_width

class Level(models.Model):
    label = models.CharField(max_length=255, unique=True, error_messages={
        'unique': 'Un niveau avec ce libellé existe déjà'
    })
    code = models.CharField(max_length=10, unique=True, error_messages={
        'unique': 'Un niveau avec ce code existe déjà'
    })
    order = models.SmallIntegerField(verbose_name='ordre')

class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='titre')
    presentation = models.TextField()
    level = models.ManyToManyField(Level, related_name='courses', verbose_name='niveau')
    authors = models.ManyToManyField(User, related_name='courses')
    cover_image = models.ImageField(upload_to='course/cover', null=True, blank=True)
    cover_image_min = models.ImageField(upload_to='course/cover/min', null=True, blank=True)
    pdf_file = models.FileField(upload_to='course/pdf')
    is_public = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def save(self, *args, **kwargs):
        if self.cover_image:
            original_filename = str(self.cover_image)
            min_file_name = 'min_' + original_filename
            self.cover_image_min.save(min_file_name, self.cover_image, save=False)
        super().save(*args, **kwargs)
        if self.cover_image_min and self.cover_image:
            crop_image(self.cover_image_min.path, 600, 400)
            edit_height_by_width(self.cover_image.path, 600)
