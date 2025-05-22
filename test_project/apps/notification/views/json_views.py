from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.managers import NotificationManager
from django_spire.notification import models


def process_json_view(request, pk: int) -> JsonResponse:
    notification = get_object_or_404(models.Notification, pk=pk)

    if notification.type == NotificationTypeChoices.PUSH:
        return JsonResponse(
            {'type': 'error', 'message': 'Push notifications not yet implemented'}
        )

    NotificationManager().process_notification(notification)
    return JsonResponse(
        {'type': 'success', 'message': 'Notification Processed'}
    )
