from __future__ import annotations

from django.urls import path

from django_spire.auth.group.views import page_views


app_name = 'page'

# Group
urlpatterns = [
    path('group/<int:pk>/detail/',
         page_views.detail_view,
         name='detail'),

    path('group/list/',
         page_views.list_view,
         name='list'),
]
