from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import QuerySet, Value, When, Case, BooleanField, IntegerField, Q
from django_spire.contrib.queryset.filter_tools import filter_by_lookup_map
from django_spire.contrib.queryset.mixins import SessionFilterQuerySetMixin
from django_spire.core.querysets import SearchQuerySetMixin

from django_spire.history.querysets import HistoryQuerySet
from django_spire.notification.choices import NotificationStatusChoices, NotificationPriorityChoices
from django_spire.notification.querysets import NotificationContentObjectQuerySet

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class AppNotificationQuerySet(
    HistoryQuerySet, NotificationContentObjectQuerySet,
    SessionFilterQuerySetMixin, SearchQuerySetMixin
):
    def annotate_is_viewed_by_user(self, user: User) -> QuerySet:
        return self.by_user(user=user).annotate(viewed=Case(
            When(views__user=user, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ))

    def ordered_by_priority_and_sent_datetime(self):
        priority_order = Case(
            When(notification__priority=NotificationPriorityChoices.LOW, then=Value(3)),
            When(notification__priority=NotificationPriorityChoices.MEDIUM, then=Value(2)),
            When(notification__priority=NotificationPriorityChoices.HIGH, then=Value(1)),
            output_field=IntegerField(),
        )
        return self.annotate(priority_order=priority_order).order_by(
            '-notification__sent_datetime',
            'priority_order'
        )

    def by_user(self, user: User) -> QuerySet:
        return self.filter(notification__user=user)

    def by_users(self, users: list[User]):
        return self.filter(notification__user__in=users)

    def exclude_viewed_by_user(self, user: User) -> QuerySet:
        return self.by_user(user=user).exclude(views__user=user)

    def is_sent(self) -> QuerySet:
        return self.filter(notification__status=NotificationStatusChoices.SENT)

    def bulk_filter(self, filter_data: dict) -> QuerySet:
        queryset = self
        filter_map = {
            'priority': 'notification__priority',
        }
        if search_term := filter_data.get("search"):
            queryset = queryset.search(search_term)
        return filter_by_lookup_map(queryset, filter_map, filter_data)

    def search(self, search_value: str) -> QuerySet:
        if search_value is None:
            return self
        return self.filter(
            Q(notification__title__icontains=search_value) |
            Q(notification__body__icontains=search_value)
        )
