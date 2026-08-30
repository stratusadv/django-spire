from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django_glue import Glue

from django_spire.notification.app.models import AppNotification
from django_spire.notification.app.navigation import AppNotificationNavigation
from django_spire.notification.app.tools import app_notification_verbose_time_since_delivered

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def app_notification_list_view(request: WSGIRequest) -> TemplateResponse:
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

    nav = AppNotificationNavigation()
    nav.page_title = 'Notification'
    nav.page_description = 'List View'
    nav.breadcrumbs.add('Notifications')
    context = nav.as_context()

    return TemplateResponse(
        request,
        context=context,
        template='django_spire/notification/app/page/list_page.html',
    )
