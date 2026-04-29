import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")
app = Celery("django_spire_test_project")
app.conf.task_default_queue = "django_spire_test_project_queue"
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(related_name='celery.tasks')
