from __future__ import annotations

from django.urls import path

from django_spire.notification.app.views import page_views


app_name = 'page'

urlpatterns = [
    path('list/', view=page_views.app_notification_list_view, name='list')
]
