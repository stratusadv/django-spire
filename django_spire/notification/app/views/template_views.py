from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from django_spire.contrib.generic_views.portal_views import infinite_scrolling_view
from django.template.response import TemplateResponse
from django_spire.notification.app.models import AppNotification


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

def notification_infinite_scroll_view(request: WSGIRequest) -> TemplateResponse:
    if isinstance(request.user, AnonymousUser):
        notifications = []

    else:
        notifications = (
            AppNotification.objects.active()
            .is_sent()
            .annotate_is_viewed_by_user(request.user)
            .select_related('notification')
            .distinct()
            .ordered_by_priority_and_sent_datetime()
        )

    body_data = json.loads(request.body.decode('utf-8'))

    return infinite_scrolling_view(
        request,
        queryset=notifications,
        queryset_name='notifications',
        context_data={
            'app_notification_list_url': body_data.get('app_notification_list_url'),
        },
        template='django_spire/notification/app/scroll/item/items.html',
    )


def notification_dropdown_template_view(request: WSGIRequest) -> TemplateResponse:
    body_data = json.loads(request.body.decode('utf-8'))

    return TemplateResponse(
        request,
        context={
            'app_notification_list_url': body_data.get('app_notification_list_url'),
            'notification_endpoint': reverse('django_spire:notification:app:template:scroll_items')
        },
        template='django_spire/notification/app/dropdown/notification_dropdown_content.html'
    )
