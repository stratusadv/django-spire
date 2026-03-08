from __future__ import annotations

from django.urls import include, path


app_name = 'api'

urlpatterns = [
    path('form/', include('django_spire.api.urls.form_urls', namespace='form')),
    path('page/', include('django_spire.api.urls.page_urls', namespace='page')),
]
