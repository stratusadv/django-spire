from __future__ import annotations

from django.urls import path

from django_spire.knowledge.collection.views import page_views


app_name = 'page'

urlpatterns = [
    path('<int:pk>/', page_views.top_level_collection_view, name='top_level'),
    path('<int:pk>/delete/', page_views.delete_view, name='delete'),
]
