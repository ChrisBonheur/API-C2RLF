from django.db import models

class Volume(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    datecreation = models.DateTimeField(auto_now_add=True)
    pages_number = models.PositiveSmallIntegerField()
    volume_year = models.PositiveIntegerField(unique=True)
    
