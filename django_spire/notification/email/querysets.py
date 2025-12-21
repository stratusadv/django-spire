from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import QuerySet, Value, When, Case, BooleanField

from django_spire.history.querysets import HistoryQuerySet
from django_spire.notification.choices import NotificationStatusChoices
from django_spire.notification.querysets import NotificationContentObjectQuerySet

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class EmailNotificationQuerySet(HistoryQuerySet, NotificationContentObjectQuerySet):
    def annotate_is_viewed_by_user(self, user: User) -> QuerySet:
        return self.by_user(user=user).annotate(viewed=Case(
            When(views__user=user, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ))

    def by_user(self, user: User) -> QuerySet:
        return self.filter(notification__user=user)

    def by_users(self, users: list[User]):
        return self.filter(notification__user__in=users)

    def exclude_viewed_by_user(self, user: User) -> QuerySet:
        return self.by_user(user=user).exclude(views__user=user)

    def is_sent(self) -> QuerySet:
        return self.filter(notification__status=NotificationStatusChoices.SENT)
