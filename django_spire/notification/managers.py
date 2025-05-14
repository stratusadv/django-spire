from django_spire.notification.app.processor import AppNotificationProcessor
from django_spire.notification.email.processor import EmailNotificationProcessor
from django_spire.notification.models import Notification
from django_spire.notification.processors.notification import NotificationProcessor
from django_spire.notification.sms.processor import SMSNotificationProcessor


class NotificationManager:
    @staticmethod
    def process_errored():
        NotificationProcessor().process_errored()

    @staticmethod
    def process_errored_app_notifications():
        AppNotificationProcessor().process_errored()

    @staticmethod
    def process_errored_email_notifications():
        EmailNotificationProcessor().process_errored()

    @staticmethod
    def process_errored_sms_notifications():
        SMSNotificationProcessor().process_errored()

    @staticmethod
    def process_notification(notification: Notification):
        NotificationProcessor().process(notification)

    @staticmethod
    def process_notifications(notifications: list[Notification]):
        NotificationProcessor().process_list(notifications)

    @staticmethod
    def process_ready_app_notifications():
        AppNotificationProcessor().process_ready()

    @staticmethod
    def process_ready_email_notifications():
        EmailNotificationProcessor().process_ready()

    @staticmethod
    def process_ready_sms_notifications():
        SMSNotificationProcessor().process_ready()

    @staticmethod
    def process_ready_to_send():
        NotificationProcessor().process_ready()
