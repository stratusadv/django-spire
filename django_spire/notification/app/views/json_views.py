from __future__ import annotations
from typing_extensions import TYPE_CHECKING


from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType

from django_spire.notification.app.models import AppNotification
from django_spire.history.viewed.models import Viewed

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def check_new_notifications_ajax_view(request: WSGIRequest) -> JsonResponse:
    notifications = (
        AppNotification.objects
        .active()
        .is_sent()
        .exclude_viewed_by_user(request.user)
    )

    return JsonResponse({
        'status': 200,
        'has_new_notifications': bool(notifications)
    })


def set_notifications_as_viewed_ajax(request: WSGIRequest) -> JsonResponse:
    notification_list = (
        AppNotification.objects
        .active()
        .is_sent()
        .by_user(request.user)
        .exclude_viewed_by_user(request.user)
    )
    ctype = ContentType.objects.get_for_model(AppNotification)
    viewed_model_objects = [
        Viewed(
            user=request.user,
            object_id=notification.id,
            content_type=ctype
        )
        for notification in notification_list
    ]

    Viewed.objects.bulk_create(viewed_model_objects)

    return JsonResponse({'status': 200, 'message': 'Notifications succesfully marked as viewed.'})
