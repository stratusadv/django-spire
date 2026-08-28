from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.http import JsonResponse
from django.template.loader import render_to_string
from django_glue import Glue

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.template.response import TemplateResponse

from django_spire.notification.app.models import AppNotification

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def dropdown_content_view(request: WSGIRequest) -> TemplateResponse:
    body_data = json.loads(request.body.decode('utf-8'))


    if isinstance(request.user, AnonymousUser):
        notifications = AppNotification.objects.none()

    else:
        notifications = (
            AppNotification.objects.active()
            .is_sent()
            .annotate_is_viewed_by_user(request.user)
            .select_related('notification')
            .distinct()
            .ordered_by_priority_and_sent_datetime()
        )

    Glue.queryset(
        request=request,
        target=notifications,
        unique_name='notifications',
        fields='__all__',
        access=Glue.Access.CHANGE
    )

    return TemplateResponse(
        request,
        context={
            'app_notification_list_url': body_data.get('app_notification_list_url'),
        },
        template='django_spire/notification/app/dropdown/notification_dropdown_content.html',
    )

@login_required()
def notification_template_render_view(request: WSGIRequest) -> JsonResponse:
    body_data = json.loads(request.body.decode('utf-8'))
    ids = body_data.get('ids', [])

    if isinstance(request.user, AnonymousUser) or not ids:
        return JsonResponse({})

    notifications = (
        AppNotification.objects.active()
        .is_sent()
        .annotate_is_viewed_by_user(request.user)
        .select_related('notification')
        .distinct()
        .ordered_by_priority_and_sent_datetime()
    )

    print(notifications)

    rendered = {
        notification.pk: render_to_string(notification.template, {'item': notification})
        for notification in notifications
    }

    return JsonResponse(rendered)
