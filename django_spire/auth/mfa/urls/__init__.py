from __future__ import annotations

from django.urls import include, path


app_name = 'mfa'

urlpatterns  = [
    path('', include('django_spire.auth.mfa.urls.page_urls', namespace='page')),
    path('', include('django_spire.auth.mfa.urls.redirect_urls', namespace='redirect')),
]
