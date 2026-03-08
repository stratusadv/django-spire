from __future__ import annotations

from django.urls import path

from django_spire.api.views import page_views


app_name = 'page'

urlpatterns = [
    path('<int:pk>/delete/', page_views.access_delete_view, name='delete'),
    path('', page_views.access_list_view, name='list'),
]
