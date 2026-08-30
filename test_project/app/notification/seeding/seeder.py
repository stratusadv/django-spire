from datetime import timedelta

from django.utils.timezone import now

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.seeding import Seeder
from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import (
    NotificationPriorityChoices,
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from django_spire.notification.models import Notification


super_user, created_ = AuthUser.objects.get_or_create(
    username='stratus',
    defaults={
        'email': 'bobert@stratusadv.com',
        'first_name': 'stratus',
        'last_name': 'stratus',
        'is_superuser': True,
        'is_staff': True,
    }
)

APP_NOTIFICATION_TEMPLATES = [
    'django_spire/notification/app/item/notification_item.html',
    'notification/item/app_alert_item.html',
    'notification/item/app_compact_item.html',
    'notification/item/app_media_item.html',
]

APP_NOTIFICATION_CONTEXT_DATA = [
    {},
    {'action_label': 'Review Now', 'action_url': '#'},
    {},
    {'action_label': 'Open', 'action_url': '#', 'category': 'System'},
]

SENT_DATETIME_START = now() - timedelta(days=30)

SENT_DATETIME_STEP = timedelta(hours=12)


class NotificationSeeder(Seeder):
    model_class = Notification

    fields_seeds = {
        'id': Seeder.exclude(),
        'user_id': Seeder.static(super_user.pk),
        'type': Seeder.static(NotificationTypeChoices.APP),
        'title': Seeder.fake.sentence(nb_words=4),
        'body': Seeder.fake.sentence(),
        'url': Seeder.llm(field_type=str, prompt='url'),
        'status': Seeder.static(NotificationStatusChoices.SENT),
        'status_message': Seeder.fake.sentence(),
        'priority': Seeder.model.random_field_choice(NotificationPriorityChoices),
        'publish_datetime': Seeder.ordered.datetime(
            start=SENT_DATETIME_START,
            step=SENT_DATETIME_STEP,
        ),
        'sent_datetime': Seeder.ordered.datetime(
            start=SENT_DATETIME_START,
            step=SENT_DATETIME_STEP,
        ),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
        'created_datetime': Seeder.exclude(),
        'content_type_id': Seeder.exclude(),
    }


class AppNotificationSeeder(Seeder):
    model_class = AppNotification

    fields_seeds = {
        'id': Seeder.exclude(),
        'notification_id': Seeder.model.ordered_queryset_foreign_key(
            Notification.objects.filter(app__isnull=True)
        ),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
        'created_datetime': Seeder.exclude(),
        'template': Seeder.ordered.choice(APP_NOTIFICATION_TEMPLATES, wrap=True),
        'context_data': Seeder.ordered.choice(APP_NOTIFICATION_CONTEXT_DATA, wrap=True),
    }
