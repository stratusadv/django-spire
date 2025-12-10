from __future__ import annotations

from django.urls import path

from django_spire.notification.app.views import template_views


app_name = 'django_spire_notification'

urlpatterns = [
    path('notficiation/dropdown/template/',
        template_views.notification_dropdown_template_view,
        name='notification_dropdown')
]
