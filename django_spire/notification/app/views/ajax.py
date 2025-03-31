from __future__ import annotations
from typing_extensions import TYPE_CHECKING

from django.http import JsonResponse
from django.urls import reverse
from django_spire.notification.app.models import AppNotification

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

def check_new_notifications_ajax_view(request: WSGIRequest) -> JsonResponse:
    notifications = AppNotification.objects.active().exclude_viewed_by_user(request.user)
        
    return JsonResponse({
        'status': 200,
        'has_new_notifications': bool(notifications)
    })
