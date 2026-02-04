from __future__ import annotations

from django.urls import path

from django_spire.metric.visual.presentation.views import template_views


app_name = 'template'

urlpatterns = [
    path('items/', template_views.items_view, name='items'),
]
