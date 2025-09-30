# sugarqube/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sugarqube.settings')

app = Celery('sugarqube')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Periodic task configuration
app.conf.beat_schedule = {
    'prewarm-prediction-cache-every-30-minutes': {
        'task': 'dashboard.tasks.prewarm_prediction_cache',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}