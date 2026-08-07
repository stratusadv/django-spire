from __future__ import annotations

from django.urls import path

from django_spire.ai.sms.views import enrollment_views, webhook_views


app_name = 'sms'

urlpatterns = [
    path(
        'enrollment/confirm/',
        enrollment_views.enrollment_confirm_view,
        name='enrollment_confirm',
    ),
    path(
        'enrollment/start/',
        enrollment_views.enrollment_start_view,
        name='enrollment_start',
    ),
    path('session/code/', enrollment_views.session_code_view, name='session_code'),
    path('webhook/', webhook_views.webhook_view, name='webhook'),
]
