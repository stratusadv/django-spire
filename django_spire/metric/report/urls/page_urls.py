from __future__ import annotations

from django.urls import path

from django_spire.metric.report.views import page_views


app_name = 'report'

urlpatterns = [
    path('',
         page_views.report_view,
         name='report'),
]
