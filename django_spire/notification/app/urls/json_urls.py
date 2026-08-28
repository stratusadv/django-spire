from __future__ import annotations

from django.urls import path

from django_spire.notification.app.views import json_views


app_name = 'json'

urlpatterns = [
    path(
        'check/', json_views.check_for_new_notifications_view, name='check_new'
    ),
    path(
        'set_viewed/',
        json_views.set_notifications_as_viewed_view,
        name='set_viewed',
    ),
]
