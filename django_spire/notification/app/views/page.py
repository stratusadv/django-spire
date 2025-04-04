from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from django_spire.notification.app.models import AppNotification

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


# def notification_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
#     notification = get_object_or_404(models.NotificationExample, pk=pk)

#     context_data = {
#         'notification': notification,
#     }

#     return portal_views.detail_view(
#         request,
#         obj=notification,
#         context_data=context_data,
#         template='notification/page/notification_detail_page.html'
#     )


# def notification_home_view(request: WSGIRequest) -> TemplateResponse:
#     template = 'notification/page/notification_home_page.html'
#     return TemplateResponse(request, template)


def app_notification_list_view(request: WSGIRequest) -> TemplateResponse:
    app_notifification_list = AppNotification.objects.by_user(request.user).order_by('-created_datetime')

    return portal_views.list_view(
        request,
        context_data={'notification_list': app_notifification_list},
        model=AppNotification,
        template='spire/notification/app/page/list_page.html'
    )
