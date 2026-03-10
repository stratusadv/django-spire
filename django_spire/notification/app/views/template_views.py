from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.template.response import TemplateResponse
from django.urls import reverse
from django_spire.contrib.generic_views.portal_views import infinite_scrolling_view
from django_spire.contrib.session.controller import SessionController
from django_spire.notification.app.constants import NOTIFICATION_FILTERING_SESSION_KEY_NAME
from django_spire.notification.app.forms import NotificationListFilterForm
from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import NotificationStatusChoices, NotificationPriorityChoices

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.core.handlers.wsgi import WSGIRequest


def _infinite_scroll_view(request: WSGIRequest, notification_queryset: QuerySet[AppNotification]) -> TemplateResponse:
    body_data = json.loads(request.body.decode('utf-8'))

    return infinite_scrolling_view(
        request,
        queryset=notification_queryset,
        queryset_name='notifications',
        context_data={
            'app_notification_list_url': body_data.get('app_notification_list_url'),
        },
        template='django_spire/notification/app/scroll/item/items.html',
    )


@login_required
def notification_infinite_scroll_view(request: WSGIRequest) -> TemplateResponse:
    if isinstance(request.user, AnonymousUser):
        return AppNotification.objects.none()

    notifications = (
        AppNotification.objects.active()
        .select_related('notification')
        .order_by('-created_datetime')
        .process_session_filter(
            request=request,
            session_key=NOTIFICATION_FILTERING_SESSION_KEY_NAME,
            form_class=NotificationListFilterForm,
        )
    )

    filter_session = SessionController(request, NOTIFICATION_FILTERING_SESSION_KEY_NAME)

    view = _infinite_scroll_view(request=request, notification_queryset=notifications)
    view.context_data.update({
        'filter_session': filter_session,
        'statuses': NotificationStatusChoices,
        'priorities': NotificationPriorityChoices,
    })
    return view


@login_required
def dropdown_infinite_scroll_view(request: WSGIRequest) -> TemplateResponse:
    if isinstance(request.user, AnonymousUser):
        return AppNotification.objects.none()

    notifications = (
        AppNotification.objects.active()
        .select_related('notification')
        .annotate_is_viewed_by_user(request.user)
        .distinct()
        .ordered_by_priority_and_sent_datetime()
    )

    view = _infinite_scroll_view(request=request, notification_queryset=notifications)
    view.context_data.update({
        'is_dropdown_item': True,
    })
    return view


@login_required
def notification_dropdown_template_view(request: WSGIRequest) -> TemplateResponse:
    body_data = json.loads(request.body.decode('utf-8'))

    return TemplateResponse(
        request,
        context={
            'app_notification_list_url': body_data.get('app_notification_list_url'),
            'notification_endpoint': reverse('django_spire:notification:app:template:dropdown_scroll_items')
        },
        template='django_spire/notification/app/dropdown/notification_dropdown_content.html'
    )
