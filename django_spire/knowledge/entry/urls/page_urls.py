from __future__ import annotations

from django.urls import path

from django_spire.knowledge.entry.views import page_views


app_name = 'page'

urlpatterns = [
    path('<int:pk>/delete/', page_views.delete_view, name='delete'),
]
