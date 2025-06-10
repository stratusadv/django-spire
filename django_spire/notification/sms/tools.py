from django_spire.notification.choices import NotificationStatusChoices
from django_spire.notification.sms.models import SmsTemporaryMedia


def update_unsent_notification_status(media_to_delete: list[SmsTemporaryMedia]) -> None:
    for media in media_to_delete:
        if media.has_unsent_notifications():
            media.sms_notifications.all().update(
                notification__status=NotificationStatusChoices.ERRORED,
                notification__status_message='SMS media expired before notification was sent',
            )
