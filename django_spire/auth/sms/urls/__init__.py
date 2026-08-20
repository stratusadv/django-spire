from __future__ import annotations

from django.urls import include, path


app_name = 'auth'

urlpatterns = [
    path('json/', include('django_spire.auth.sms.urls.json_urls', namespace='json')),
]
