# Generated by Django 3.0.8 on 2020-07-13 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainsite', '0007_auto_20200710_2319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='show',
            name='webid',
        ),
        migrations.AlterField(
            model_name='show',
            name='airing',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='show',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posters/'),
        ),
        migrations.AlterField(
            model_name='show',
            name='plot',
            field=models.CharField(default='To Add', max_length=400),
        ),
        migrations.AlterField(
            model_name='show',
            name='year',
            field=models.IntegerField(default=0),
        ),
    ]
