from __future__ import annotations
from typing import TYPE_CHECKING
from django.db.models import QuerySet, Value, When, Case, BooleanField

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class AppNotificationQuerySet(QuerySet):
    def active(self) -> QuerySet:
        return self.filter(is_active=True, is_deleted=False)

    def by_user(self, user: User) -> QuerySet:
        return self.filter(notification__user=user)

    def exclude_viewed_by_user(self, user: User) -> QuerySet:
        return self.by_user(user=user).exclude(views__user=user)

    def annotate_is_viewed_by_user(self, user: User) -> QuerySet:
        return self.by_user(user=user).annotate(viewed=Case(
            When(views__user=user, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ))
