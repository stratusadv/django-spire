from __future__ import annotations

from django.urls import path

from django_spire.metric.visual.signage.views import page_views

app_name = 'page'

urlpatterns = [
    path('list/', page_views.list_view, name='list'),
    path('<int:pk>/detail/', page_views.detail_view, name='detail'),
    path('display/<uuid:key>/', page_views.display_view, name='display'),
    path('test_display_resolution/<uuid:key>/', page_views.test_display_resolution_view, name='test_display_resolution'),
]
