from __future__ import annotations

from django.urls import path

from django_spire.auth.sms.views.json_views import (
    enrollment_confirm_view,
    enrollment_start_view,
)

app_name = 'enrollment'

urlpatterns = [
    path('confirm/', enrollment_confirm_view, name='confirm'),
    path('start/', enrollment_start_view, name='start'),
]
