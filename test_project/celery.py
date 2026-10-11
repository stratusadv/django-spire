import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.settings')
app = Celery('django_spire_test_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=3600,
    task_soft_time_limit=3500,
    worker_max_tasks_per_child=200,  # leak insurance w/ threads pool
    worker_deduplicate_successful_tasks=True,  # needs acks_late + persistent backend
    broker_connection_retry_on_startup=True,
)
app.conf.task_default_queue = 'django_spire_test_project_queue'
