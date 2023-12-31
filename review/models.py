from typing import Iterable, Optional
from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os

from apiC2rlf.utils import edit_height_by_width

class Volume(models.Model):
    number = models.PositiveSmallIntegerField()
    datecreation = models.DateTimeField(auto_now_add=True)
    pages_number = models.PositiveSmallIntegerField()
    volume_year = models.PositiveIntegerField()
    
class Numero(models.Model):
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE)
    datecreation = models.DateField(auto_now_add=True)
    label = models.CharField(max_length=100, null=True, blank=True)
    number = models.PositiveSmallIntegerField(unique=True)

    def save(self, *args, **kwargs) -> None:
        label_value = f"Numéro {self.number} du volume {self.volume.number}"
        self.label = label_value
        super(Numero, self).save(*args, **kwargs)

class Sommaire(models.Model):
    title = models.CharField(max_length=1000)
    label = models.CharField(max_length=50, null=True, blank=True)
    presentation = models.TextField()
    numero = models.OneToOneField(Numero, on_delete=models.CASCADE)
    picture = models.ImageField(null=True, blank=True, upload_to="pictures/sommaires")
    pdf_file = models.FileField(upload_to="pdfs/sommaires")
    author = models.ManyToManyField(User, related_name='sommaires')

    def save(self, *args, **kwargs) -> None:
        self.label = f"sommaire lié au numero {self.numero.number}"
        super(Sommaire, self).save(*args, **kwargs)
        if self.picture:
            edit_height_by_width(self.picture.path, 400)

class TypeSource(models.Model):
    type_name = models.CharField(max_length=50)

class Source(models.Model):
    authors = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    year_publication = models.CharField(max_length=4, null=True, blank=True)
    editor = models.CharField(max_length=255, null=True, blank=True)
    type_source = models.ForeignKey(TypeSource, on_delete=models.PROTECT, null=True, blank=True)

class Reference(models.Model):
    source = models.OneToOneField(Source, on_delete=models.PROTECT, null=True, blank=True)
    volume = models.CharField(max_length=255, null=True, blank=True)
    publication = models.CharField(max_length=255, null=True, blank=True)
    page_begin = models.IntegerField(null=True, blank=True)
    page_end = models.IntegerField(null=True, blank=True)
    edition_ref = models.CharField(max_length=255, null=True, blank=True)

class Article(models.Model):
    class State(models.IntegerChoices):
        INITIALISATION = 1
        PARRUTION = 2
        PUBLICATION = 3
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    title_fr = models.CharField(max_length=255)
    title_ang = models.CharField(max_length=255, null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_accept = models.DateTimeField(null=True, blank=True)
    date_publication = models.DateTimeField(null=True, blank=True)
    abstract_fr = models.TextField()
    abstract_ang = models.TextField(null=True, blank=True)
    file_submit = models.FileField(upload_to="files-submit/articles", null=True, blank=True)
    pdf_file = models.FileField(upload_to="files-submit/articles", null=True, blank=True)
    numero = models.ForeignKey(Numero, on_delete=models.CASCADE, null=True, blank=True)
    keywords_fr = models.TextField(null=True, blank=True)
    keywords_ang = models.TextField(null=True, blank=True)
    state = models.IntegerField(choices=State.choices, default=State.INITIALISATION)
    authors = models.ManyToManyField(User, related_name='articles')
    page_begin = models.IntegerField(null=True, blank=True)
    page_end = models.IntegerField(null=True, blank=True)
    doi_link = models.TextField(null=True, blank=True)
    orcid_link = models.CharField(max_length=255, null=True, blank=True)
    counter_download = models.IntegerField(default=0)
    image_cover = models.ImageField(upload_to='pictures/articles-cover', null=True, blank=True)
    references = models.ManyToManyField(Reference, blank=True)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

@receiver(post_delete, sender=Article)
def post_delete_receiver(sender, instance, **kwargs):
    if instance.file_submit:
        res = os.system(f"rm media/{instance.file_submit.path}")
    if instance.pdf_file:
        os.system(f"rm media/{instance.pdf_file.path}")

"""
@receiver(pre_save, sender=Article)
def post_delete_receiver(sender, instance, **kwargs):
    if instance.file_submit:
        res = os.system(f"rm media/{instance.file_submit}")
"""