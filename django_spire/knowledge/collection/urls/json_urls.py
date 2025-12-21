from __future__ import annotations

from django.urls import path

from django_spire.knowledge.collection.views import json_views


app_name = 'json'

urlpatterns = [
    path('reorder/', json_views.reorder_view, name='reorder'),
]
