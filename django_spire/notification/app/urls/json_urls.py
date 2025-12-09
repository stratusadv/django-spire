from __future__ import annotations

from django.urls import path

from django_spire.notification.app.views import json_views


app_name = 'django_spire_notification'

urlpatterns = [
    path('check/notification/ajax/',
         json_views.check_new_notifications_ajax_view,
         name='check_new'),

    path('set_viewed/notification/ajax/',
         json_views.set_notifications_as_viewed_ajax,
         name='set_viewed'),
]
