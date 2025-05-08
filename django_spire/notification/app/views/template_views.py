from __future__ import annotations

import json

from django.urls import reverse

from typing_extensions import TYPE_CHECKING

from django.template.response import TemplateResponse

from django_spire.notification.app.models import AppNotification

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def notification_delete_template_view(
    request: WSGIRequest,
    pk: int
) -> TemplateResponse:
    return TemplateResponse(
        request,
        context={
            'form_title': 'Delete Notification',
            'form_description': 'Are you sure you would like to delete this notification?',
            'form_action': reverse(
                'django_spire:notification:group:redirect:delete',
                kwargs={'pk': pk}
            ),
            'return_url': reverse(
                'django_spire:notification:group:page:list'
            ),
        },
        template='django_spire/modal/content/dispatch_modal_delete_confirmation_content.html'
    )


def notification_dropdown_template_view(request: WSGIRequest) -> TemplateResponse:
    app_notification_list = (
        AppNotification.objects.active()
        .annotate_is_viewed_by_user(request.user)
        .order_by("-created_datetime")
        .select_related("notification")
        .distinct()
    )

    body_data = json.loads(request.body.decode('utf-8'))

    return TemplateResponse(
        request,
        context={
            'app_notification_list': app_notification_list,
            'app_notification_list_url': body_data.get('app_notification_list_url'),
        },
        template='django_spire/notification/app/dropdown/notification_dropdown_content.html'
    )
