# Generated by Django 3.0.8 on 2020-07-20 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mylogin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Applications',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('approved', models.BooleanField(default=False)),
            ],
        ),
    ]
