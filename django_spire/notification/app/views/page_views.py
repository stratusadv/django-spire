from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.session.controller import SessionController
from django_spire.notification.app.constants import NOTIFICATION_FILTERING_SESSION_KEY_NAME
from django_spire.notification.app.forms import NotificationListFilterForm
from django_spire.notification.app.models import AppNotification
from django_spire.notification.app.navigation import AppNotificationNavigation
from django_spire.notification.choices import NotificationPriorityChoices

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def app_notification_list_view(request: WSGIRequest) -> TemplateResponse:
    (
        AppNotification.objects.active()
        .is_sent()
        .annotate_is_viewed_by_user(request.user)
        .select_related('notification')
        .distinct()
        .process_session_filter(
            request=request,
            session_key=NOTIFICATION_FILTERING_SESSION_KEY_NAME,
            form_class=NotificationListFilterForm,
        )
    )

    nav = AppNotificationNavigation()
    nav.page_title = 'Notification'
    nav.page_description = 'List View'
    nav.breadcrumbs.add('Notifications')
    context = nav.as_context()
    context['notification_endpoint'] = reverse(
        'django_spire:notification:app:template:scroll_items'
    )
    context['filter_session'] = SessionController(request, NOTIFICATION_FILTERING_SESSION_KEY_NAME)
    context['priority_choices'] = json.dumps(NotificationPriorityChoices.choices[::-1])
    return TemplateResponse(request, context=context, template='django_spire/page/page.html')
