from __future__ import annotations

from django.urls import path

from django_spire.auth.mfa.views import redirect_views


app_name = 'redirect'

urlpatterns = [
    path('notification/',
         redirect_views.mfa_notification_redirect_view,
         name='notification'),
]
