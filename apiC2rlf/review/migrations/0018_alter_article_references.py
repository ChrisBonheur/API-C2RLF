# Generated by Django 3.2.20 on 2023-09-17 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0017_auto_20230917_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='references',
            field=models.ManyToManyField(blank=True, to='review.Reference'),
        ),
    ]