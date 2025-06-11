from django_spire.notification.choices import NotificationStatusChoices
from django_spire.notification.sms.models import SmsTemporaryMedia


def update_unsent_notification_status_for_deleted_temporary_media(
    temporary_media_to_delete: list[SmsTemporaryMedia]
):
    for temporary_media in temporary_media_to_delete:
        if temporary_media.has_unsent_notifications():
            temporary_media.sms_notifications.all().update(
                notification__status=NotificationStatusChoices.ERRORED,
                notification__status_message='SMS temporary media expired before notification was sent',
            )
