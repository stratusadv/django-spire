from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django_glue import Glue

from django_spire.notification.app.models import AppNotification
from django_spire.notification.app.tools import app_notification_verbose_time_since_delivered

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

    computed_attributes = {
        'time_since_delivered': app_notification_verbose_time_since_delivered,
    }

    Glue.queryset(
        request=request,
        target=notifications,
        unique_name='notifications',
        fields='__all__',
        access=Glue.Access.CHANGE,
        computed_attributes=computed_attributes,
    )

    context = {'app_notification_list_url': body_data.get('app_notification_list_url')}

    return TemplateResponse(
        request,
        context=context,
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
        .filter(pk__in=ids)
        .distinct()
    )

    rendered = {}

    for notification in notifications:
        context = {'item': notification}
        rendered[notification.pk] = render_to_string(notification.template, context)

    return JsonResponse(rendered)
