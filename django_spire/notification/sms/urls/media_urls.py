from __future__ import annotations

from django.urls import path

from django_spire.notification.sms.views import media_views


app_name = 'media'

urlpatterns = [
    path('<uuid:external_access_key>/temporary_media/',
         media_views.external_temporary_media_view,
         name='temporary_media')
]
