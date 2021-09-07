from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

from django.conf import settings

from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoproj.settings')

app = Celery('djangoproj')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks(settings.INSTALLED_APPS)