from __future__ import annotations

from django.urls import path

from django_spire.metric.domain.statistic.views import page_views

app_name = 'page'

urlpatterns = [
    path('list/', page_views.list_view, name='list'),
    path('<int:pk>/detail/', page_views.detail_view, name='detail'),
    path('group/list/', page_views.group_list_view, name='group_list'),
    path('group/<int:pk>/detail/', page_views.group_detail_view, name='group_detail'),
]
