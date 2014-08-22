'''
@summary: http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
'''
from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

from os.path import abspath, basename, dirname

########## PATH CONFIGURATION
# Site name:
SITE_NAME = basename(dirname(abspath(__file__)))

# set the default Django settings module for the 'celery' program.
# Run this from commandline instead (export/set DJANGO_SETTINGS_MODULE=val)
## os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{0}.settings.local'.format(SITE_NAME))

app = Celery(SITE_NAME)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))