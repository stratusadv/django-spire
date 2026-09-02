from __future__ import annotations

from django.urls import include, path


app_name = 'core'

urlpatterns = [path('search/', include('django_spire.core.urls.search_urls', namespace='search'))]
