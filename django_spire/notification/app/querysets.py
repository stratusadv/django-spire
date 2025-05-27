from __future__ import annotations
from typing import TYPE_CHECKING
from django.db.models import QuerySet, Value, When, Case, BooleanField, IntegerField

from django_spire.history.querysets import HistoryQuerySet
from django_spire.notification.choices import NotificationStatusChoices, NotificationPriorityChoices

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class AppNotificationQuerySet(HistoryQuerySet):
    def annotate_is_viewed_by_user(self, user: User) -> QuerySet:
        return self.by_user(user=user).annotate(viewed=Case(
            When(views__user=user, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ))
    def ordered_by_priority(self):
        priority_order = Case(
            When(notification__priority=NotificationPriorityChoices.LOW, then=Value(3)),
            When(notification__priority=NotificationPriorityChoices.MEDIUM, then=Value(2)),
            When(notification__priority=NotificationPriorityChoices.HIGH, then=Value(1)),
            output_field=IntegerField(),
        )
        return self.annotate(priority_order=priority_order).order_by('priority_order')

    def by_user(self, user: User) -> QuerySet:
        return self.filter(notification__user=user)

    def exclude_viewed_by_user(self, user: User) -> QuerySet:
        return self.by_user(user=user).exclude(views__user=user)

    def is_sent(self) -> QuerySet:
        return self.filter(notification__status=NotificationStatusChoices.SENT)
