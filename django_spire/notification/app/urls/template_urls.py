from __future__ import annotations

from django.urls import path

from django_spire.notification.app.views import template_views

app_name = 'template'

urlpatterns = [
    path(
        'dropdown/',
        template_views.dropdown_content_view,
        name='notification_dropdown',
    ),
    path(
        'render-templates/',
        template_views.notification_template_render_view,
        name='render_templates',
    ),
]
