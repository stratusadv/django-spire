from django_spire.notification.app.processor import AppNotificationProcessor
from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.email.processor import EmailNotificationProcessor
from django_spire.notification.sms.processor import SMSNotificationProcessor

NotificationProcessorMap = {
    NotificationTypeChoices.APP: AppNotificationProcessor,
    NotificationTypeChoices.EMAIL: EmailNotificationProcessor,
    NotificationTypeChoices.SMS: SMSNotificationProcessor,
}
