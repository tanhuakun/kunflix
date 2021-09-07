# Generated by Django 3.0.8 on 2020-07-21 21:07

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainsite', '0015_show_max_episode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requests',
            name='image',
            field=models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='C:\\ServerRelated\\posters\\'), upload_to='reqposters/'),
        ),
        migrations.AlterField(
            model_name='show',
            name='image',
            field=models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='C:\\ServerRelated\\posters\\'), upload_to='posters/'),
        ),
        migrations.AlterField(
            model_name='show',
            name='max_episode',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]
