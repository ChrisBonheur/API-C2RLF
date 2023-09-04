from typing import Iterable, Optional
from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint

class Volume(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    datecreation = models.DateTimeField(auto_now_add=True)
    pages_number = models.PositiveSmallIntegerField()
    volume_year = models.PositiveIntegerField(unique=True)
    

class Numero(models.Model):
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE)
    datecreation = models.DateField(auto_now_add=True)
    label = models.CharField(max_length=100)
    number = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            UniqueConstraint(fields=['number', 'volume'], name='unique_numero_by_volume')
        ]

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
