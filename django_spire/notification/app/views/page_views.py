from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.urls import reverse

from django_spire.contrib.generic_views import portal_views

from django_spire.notification.app.models import AppNotification

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@login_required()
def app_notification_list_view(request: WSGIRequest) -> TemplateResponse:
    return portal_views.list_view(
        request,
        context_data={'notification_endpoint': reverse('django_spire:notification:app:template:scroll_items')},
        model=AppNotification,
        template='django_spire/notification/app/page/list_page.html'
    )
