# #celery.py(add the exact code, just change your project name)
# # from __future__ import absolute_import
# # import os
# # # from celery import Celery
from django.conf import settings
from celery.schedules import crontab
from emailreport.tasks import send_daily_reports_task
# # # set the default Django settings module for the 'celery' program.

import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tcubesa.settings')

app = Celery('tcubesa',broker='redis://localhost:6379/0')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda:settings.INSTALLED_APPS)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# app.conf.beat_schedule = {
#     'send_daily_reports_task': {
#         'task': 'emailreport.tasks.send_daily_reports_task',  # Replace with the actual path to your task
#         'schedule': crontab(minute='*/1'),  # Daily at 5 PM (hour=17, minute=0)
#     }
# }