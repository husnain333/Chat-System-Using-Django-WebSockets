from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatproject.settings')

app = Celery('chatproject')
app.conf.enable_utc = False
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     'task-every-hour': {
#         'task': 'chat.tasks.taskEveryHour',
#         'schedule': crontab(minute=20),  
#     },
# }

# IN SHELL
# from django_celery_beat.models import PeriodicTask, IntervalSchedule
# schedule, _ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.HOURS)
# PeriodicTask.objects.create(
#     interval=schedule,
#     name='Hourly Task',
#     task='chat.tasks.taskEveryHour',
#     enabled=True
# )

