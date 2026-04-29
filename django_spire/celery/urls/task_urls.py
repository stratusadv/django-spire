from __future__ import annotations

from django.urls import path

from django_spire.celery.views import task_views


app_name = 'task'

urlpatterns = [
    path('item/<str:task_id>/', task_views.task_item_view, name='item'),
    path('item_list/', task_views.task_item_list_view, name='item_list'),
    path('toast/<str:task_id>/', task_views.task_toast_view, name='toast'),
    path('toast_list/', task_views.task_toast_list_view, name='toast_list'),
]
