from __future__ import annotations

from django.urls import include, path


app_name = 'celery'

urlpatterns = [
    path('json/', include('django_spire.celery.urls.json_urls', namespace='json')),
]
