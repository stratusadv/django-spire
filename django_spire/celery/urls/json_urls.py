from __future__ import annotations

from django.urls import path

from django_spire.celery.views import json_views


app_name = 'json'

urlpatterns = [
    path('task_info/', json_views.task_info_view, name='task_info'),
]
