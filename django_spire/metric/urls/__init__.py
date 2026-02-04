from __future__ import annotations

from django.urls import include, path


app_name = 'metric'

urlpatterns = [
    path('report/', include('django_spire.metric.report.urls', namespace='report')),
    path('api/')
]
