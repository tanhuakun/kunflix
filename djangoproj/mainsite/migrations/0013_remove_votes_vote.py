# Generated by Django 3.0.8 on 2020-07-17 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainsite', '0012_auto_20200717_2112'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='votes',
            name='vote',
        ),
    ]
