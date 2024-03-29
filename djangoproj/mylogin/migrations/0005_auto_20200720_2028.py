# Generated by Django 3.0.8 on 2020-07-20 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mylogin', '0004_auto_20200720_1801'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegisterAttempts',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ip_address', models.CharField(max_length=80)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='invites',
            name='id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='invites',
            name='code',
            field=models.CharField(max_length=20),
        ),
    ]
