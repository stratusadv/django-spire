from __future__ import annotations

from django.urls import include, path


app_name = 'sms'

urlpatterns = [
    path('media/', include('django_spire.notification.sms.urls.media_urls', namespace='media')),
]
