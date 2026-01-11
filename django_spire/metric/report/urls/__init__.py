from __future__ import annotations

from django.urls import include, path


app_name = 'report'

urlpatterns = [
    path('page/', include('django_spire.metric.report.urls.page_urls', namespace='page')),
]
