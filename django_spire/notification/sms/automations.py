from __future__ import annotations

from django_spire.notification.sms.models import SmsTemporaryMedia
from django_spire.notification.sms.tools import update_unsent_notification_status_for_deleted_temporary_media


def clear_sms_temporary_media():
    media_to_delete = (
        SmsTemporaryMedia.objects
        .is_ready_for_deletion()
        .active()
        .prefetch_related('sms_notifications__notification')
    )

    update_unsent_notification_status_for_deleted_temporary_media(media_to_delete)

    SmsTemporaryMedia.objects.bulk_delete(media_to_delete)
