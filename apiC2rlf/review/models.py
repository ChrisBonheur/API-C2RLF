from django.db import models

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
