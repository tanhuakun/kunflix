# Generated by Django 3.0.7 on 2020-07-03 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainsite', '0002_auto_20200703_2349'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='show',
            name='group',
        ),
        migrations.AddField(
            model_name='show',
            name='category',
            field=models.CharField(default='English', max_length=10),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Group',
        ),
    ]
