from __future__ import annotations

from django.urls import path

from django_spire.celery.views import task_views


app_name = 'task'

urlpatterns = [
    path('<str:task_id>/', task_views.task_view, name='toast'),
    path('list/<str:reference_key>/', task_views.task_list_view, name='toast_list'),
]
