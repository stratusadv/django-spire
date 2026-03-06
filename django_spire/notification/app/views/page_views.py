from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.urls import reverse

from django_spire.contrib.generic_views import portal_views
from django_spire.contrib.session.controller import SessionController
from django_spire.notification.app.constants import NOTIFICATION_FILTERING_SESSION_KEY_NAME
from django_spire.notification.app.forms import NotificationListFilterForm

from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import NotificationStatusChoices, NotificationPriorityChoices

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@login_required()
def app_notification_list_view(request: WSGIRequest) -> TemplateResponse:
    AppNotification.objects.process_session_filter(
        request=request,
        session_key=NOTIFICATION_FILTERING_SESSION_KEY_NAME,
        form_class=NotificationListFilterForm,
    )

    return portal_views.list_view(
        request,
        context_data={
            'notification_endpoint': reverse('django_spire:notification:app:template:scroll_items'),
            'filter_session': SessionController(request, NOTIFICATION_FILTERING_SESSION_KEY_NAME),
            'status_choices': json.dumps(NotificationStatusChoices.choices[2:]),
            'priority_choices': json.dumps(NotificationPriorityChoices.choices[::-1]),
        },
        model=AppNotification,
        template='django_spire/notification/app/page/list_page.html'
    )
