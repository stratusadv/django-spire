from __future__ import annotations

from django.urls import path

from django_spire.knowledge.entry.version.views import redirect_views


app_name = 'redirect'

urlpatterns = [
    path('<int:pk>/publish/', redirect_views.publish_view, name='publish'),
]
