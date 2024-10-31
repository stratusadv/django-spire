from typing import Union

from django_spire.notification.models import Notification


def create_notification(
        email: str,
        title: str,
        body: str,
        url: Union[str, None] = None,
        name: Union[str, None] = None
):
    return Notification.objects.create(
        email=email,
        name=name,
        title=title,
        body=body,
        url=url
    )
