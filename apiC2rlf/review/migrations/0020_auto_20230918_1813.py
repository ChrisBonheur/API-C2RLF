# Generated by Django 3.2.20 on 2023-09-18 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0019_auto_20230918_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='keywords_ang',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='keywords_fr',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='orcid_link',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]