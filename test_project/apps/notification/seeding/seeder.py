

from django.contrib.auth.models import User
from django.utils import timezone

from django_spire.contrib.seeding import DjangoModelSeeder
from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.models import Notification


class NotificationSeeder(DjangoModelSeeder):
    model_class = Notification
    default_to = 'faker'
    fields = {
        'id': 'exclude',
        'is_active': 'True',
        'is_deleted': 'False',
        'created_datetime': 'exclude',
        'title': ('faker', 'word'),
        'body': ('faker', 'sentence'),
        'url': ('faker', 'url'),
        'status_message': ('faker', 'sentence'),
        'content_type_id': 'exclude',
        'user_id': 1, # stratus,Bob,Robertson,bobert@stratusadv.com
        'publish_datetime': timezone.now(),
        'sent_datetime': timezone.now(),
    }

    @classmethod
    def seed_app_notification(cls, count=10):
        notifications = cls.seed_database(
            count=count,
            fields=cls.fields | {
                'type': NotificationTypeChoices.APP,
            },
        )
        return notifications


class AppNotificationSeeder(DjangoModelSeeder):
    model_class = AppNotification
    default_to = 'faker'
    fields = {
        'id': 'exclude',
        'is_active': 'True',
        'is_deleted': 'False',
        'created_datetime': 'exclude',
        'template': 'django_spire/notification/app/item/notification_item.html',
        'context_data': {},
    }

    @classmethod
    def seed_database(cls, count=10, fields={}):
        app_notifications = super().seed_database(
            count=count,
            fields=cls.fields | {
                'notification_id': ('custom', 'in_order', {'values': [user.id for user in User.objects.all()]}),
            },
        )
        return app_notifications
