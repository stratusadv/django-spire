from __future__ import annotations

from django.urls import path

from django_spire.theme.views import json_views


app_name = 'json'

urlpatterns = [
    path('get_config/', json_views.get_config, name='get_config'),
    path('set_theme/', json_views.set_theme, name='set_theme'),
]
