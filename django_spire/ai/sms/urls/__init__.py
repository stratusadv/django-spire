from __future__ import annotations

from django.urls import path

from django_spire.ai.sms.views import webhook_views


app_name = 'sms'

urlpatterns = [path('webhook/', webhook_views.webhook_view, name='webhook')]
