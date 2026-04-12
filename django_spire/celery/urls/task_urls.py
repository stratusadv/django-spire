from __future__ import annotations

from django.urls import path

from django_spire.celery.views import task_views


app_name = 'json'

urlpatterns = [
    path('<str:key>/', task_views.task_view, name='task'),
    path('list/<str:object_hash>/', task_views.task_list_view, name='list'),
]
