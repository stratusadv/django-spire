from __future__ import annotations

from django_spire.notification.models import Notification


def create_notification(
        email: str,
        title: str,
        body: str,
        url: str | None = None,
        name: str | None = None
) -> Notification:
    return Notification.objects.create(
        email=email,
        name=name,
        title=title,
        body=body,
        url=url
    )
