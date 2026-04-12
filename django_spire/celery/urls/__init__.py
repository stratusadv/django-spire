from __future__ import annotations

from django.urls import include, path


app_name = 'celery'

urlpatterns = [
    path('task/', include('django_spire.celery.urls.task_urls', namespace='task')),
]
