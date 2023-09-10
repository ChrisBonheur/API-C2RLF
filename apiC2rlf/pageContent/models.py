from django.db import models

class PageContent(models.Model):
    title = models.CharField(max_length=50, unique=True)
    content = models.TextField(null=True, blank=True)
    date_update = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='pages-content', null=True, blank=True)
    order = models.SmallIntegerField(default=1)


