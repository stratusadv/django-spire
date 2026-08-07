from __future__ import annotations

from django.urls import include, path

from django_spire.auth.sms.views.json_views import session_code_view

app_name = 'auth'

urlpatterns = [
    path(
        'enrollment/',
        include('django_spire.auth.sms.urls.json_urls', namespace='enrollment'),
    ),
    path('session/code/', session_code_view, name='session_code'),
]
