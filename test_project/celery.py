import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.settings')
app = Celery('django_spire_test_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(task_track_started=True)
app.conf.task_default_queue = 'django_spire_test_project_queue'
