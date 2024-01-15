"""Celery configurations are specified here."""

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'rightorigins_v3.settings.local')

app = Celery(
    'rightorigins_v3',
    broker='redis://127.0.0.1:6379',
    backend='redis://127.0.0.1:6379',
    )

BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'Asia/Calcutta'
app.autodiscover_tasks(['utilities',])
