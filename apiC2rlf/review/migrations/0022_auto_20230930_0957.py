# Generated by Django 3.2.20 on 2023-09-30 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0021_auto_20230926_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volume',
            name='number',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='volume',
            name='volume_year',
            field=models.PositiveIntegerField(),
        ),
    ]