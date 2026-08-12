from __future__ import annotations

from django.urls import path

from django_spire.auth.sms.views import json_views

app_name = 'json'

urlpatterns = [
    path('session/code/', json_views.session_code_view, name='session_code'),
    path(
        'verification-confirm/',
        json_views.verification_confirm_view,
        name='verification_confirm'
    ),
    path(
        'verification-start/',
        json_views.verification_start_view,
        name='verification_start'
    ),
]
