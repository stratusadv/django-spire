from __future__ import annotations

from django.urls import path

from django_spire.knowledge.entry.version.views import page_views


app_name = 'page'

urlpatterns = [
    path('<int:pk>/editor/', page_views.editor_view, name='editor'),
]
