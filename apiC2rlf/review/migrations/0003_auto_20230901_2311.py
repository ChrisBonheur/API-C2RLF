# Generated by Django 3.2.20 on 2023-09-01 23:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('review', '0002_numero'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sommaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1000)),
                ('label', models.CharField(blank=True, max_length=50, null=True)),
                ('presentation', models.TextField()),
                ('picture', models.ImageField(blank=True, null=True, upload_to='pictures/sommaires')),
                ('pdf_file', models.FileField(upload_to='pdfs/sommaires')),
            ],
        ),
        migrations.AddConstraint(
            model_name='numero',
            constraint=models.UniqueConstraint(fields=('number', 'volume'), name='unique_numero_by_volume'),
        ),
        migrations.AddField(
            model_name='sommaire',
            name='author',
            field=models.ManyToManyField(related_name='sommaires', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sommaire',
            name='numero',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='review.numero'),
        ),
    ]