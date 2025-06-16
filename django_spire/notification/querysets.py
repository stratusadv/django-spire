from collections import defaultdict

from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth.models import User
from django.db.models import QuerySet, Q, Model
from django.utils.timezone import now

from django_spire.history.querysets import HistoryQuerySet
from django_spire.notification.choices import (
    NotificationStatusChoices,
    NotificationTypeChoices,
    NotificationPriorityChoices,
)


class NotificationQuerySet(HistoryQuerySet):
    def app_notifications(self):
        return self.filter(type=NotificationTypeChoices.APP)

    def by_content_object(self, content_object: type[Model]):
        return self.filter(
            content_type=get_content_type_for_model(content_object),
            object_id=content_object.pk,
        )

    def by_content_objects(self, content_objects: list[type[Model]]):
        if not content_objects:
            return self.none()

        content_type_to_object_ids = defaultdict(list)

        for content_object in content_objects:
            content_type_to_object_ids[
                get_content_type_for_model(content_object)
            ].append(content_object.pk)

        queries = Q()
        for content_type, object_ids in content_type_to_object_ids.items():
            queries |= Q(
                content_type=content_type,
                object_id__in=object_ids
            )

        return self.filter(queries)

    def by_user(self, user: User):
        return self.filter(user=user)

    def by_users(self, users: list[User]):
        return self.filter(user__in=users)

    def email_notifications(self):
        return self.filter(type=NotificationTypeChoices.EMAIL)

    def errored(self):
        return self.filter(status=NotificationStatusChoices.ERRORED)

    def failed(self):
        return self.filter(status=NotificationStatusChoices.FAILED)

    def high_priority(self):
        return self.filter(priority=NotificationPriorityChoices.HIGH)

    def low_priority(self):
        return self.filter(priority=NotificationPriorityChoices.LOW)

    def medium_priority(self):
        return self.filter(priority=NotificationPriorityChoices.MEDIUM)

    def pending(self):
        return self.filter(status=NotificationStatusChoices.PENDING)

    def processing(self):
        return self.filter(status=NotificationStatusChoices.PROCESSING)

    def push_notifications(self):
        return self.filter(status=NotificationTypeChoices.PUSH)

    def ready_to_send(self):
        return self.pending().filter(publish_datetime__lte=now())

    def sent(self):
        return self.filter(status=NotificationStatusChoices.SENT)

    def sms_notifications(self):
        return self.filter(type=NotificationTypeChoices.SMS)

    def unsent(self):
        return self.filter(status__in=[NotificationStatusChoices.PENDING, NotificationStatusChoices.PROCESSING])


class NotificationContentObjectQuerySet(QuerySet):
    def by_notification_content_object(self, content_object: type[Model]):
        return self.filter(
            notification__content_type=get_content_type_for_model(content_object),
            notification__object_id=content_object.pk,
        )

    def by_notification_content_objects(self, content_objects: list[type[Model]]):
        if not content_objects:
            return self.none()

        content_type_to_object_ids = defaultdict(list)

        for content_object in content_objects:
            content_type_to_object_ids[
                get_content_type_for_model(content_object)
            ].append(content_object.pk)

        queries = Q()
        for content_type, object_ids in content_type_to_object_ids.items():
            queries |= Q(
                notification__content_type=content_type,
                notification__object_id__in=object_ids
            )

        return self.filter(queries)
