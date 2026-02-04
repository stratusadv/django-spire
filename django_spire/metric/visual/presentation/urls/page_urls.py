from __future__ import annotations

from django.urls import path

from django_spire.metric.visual.presentation.views import page_views


app_name = 'page'

urlpatterns = [
    path('list/', page_views.list_view, name='list'),
    path('<int:pk>/detail/', page_views.detail_view, name='detail'),
]
