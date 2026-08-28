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


class NotificationSeeder(Seeder):
    model_class = Notification

    fields_seeds = {
        'id': Seeder.exclude(),
        'user_id': Seeder.static(super_user.pk),
        'type': Seeder.model.random_field_choice(NotificationTypeChoices),
        'title': Seeder.fake.sentence(nb_words=1),
        'body': Seeder.fake.sentence(),
        'url': Seeder.llm(field_type=str, prompt='url'),
        'status': Seeder.model.random_field_choice(NotificationStatusChoices),
        'status_message': Seeder.fake.sentence(),
        'priority': Seeder.model.random_field_choice(NotificationPriorityChoices),
        'publish_datetime': Seeder.fake.date_time_between(start_date='now', end_date='now'),
        'sent_datetime': Seeder.fake.date_time_between(start_date='now', end_date='now'),
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
        'template': Seeder.static('django_spire/notification/app/item/notification_item.html'),
        'context_data': Seeder.static({}),
    }
