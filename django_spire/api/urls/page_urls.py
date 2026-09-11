from __future__ import annotations

from django.urls import path

from django_spire.api.views import page_views


app_name = 'page'

urlpatterns = [
    path('', page_views.access_list_view, name='list'),
    path('<int:pk>/detail/', page_views.access_detail_view, name='detail'),
]
