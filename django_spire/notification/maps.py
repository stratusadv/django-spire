from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.push.models import PushNotification
from django_spire.notification.sms.models import SmsNotification

NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP: dict[NotificationTypeChoices, type] = {
    NotificationTypeChoices.APP: AppNotification,
    NotificationTypeChoices.EMAIL: EmailNotification,
    NotificationTypeChoices.PUSH: PushNotification,
    NotificationTypeChoices.SMS: SmsNotification
}