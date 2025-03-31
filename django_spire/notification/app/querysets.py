from __future__ import annotations
from typing import TYPE_CHECKING
from django.db.models import QuerySet

if TYPE_CHECKING:
    from django.contrib.auth.models import User

class AppNotificationQuerySet(QuerySet):
    def active(self) -> QuerySet:
        return self.filter(is_active=True, is_deleted=False)

    def by_user(self, user: User) -> QuerySet:
        return self.filter(user=user)

    def exclude_viewed_by_user(self, user: User) -> QuerySet:
        return self.by_user(user=user).exclude(views__user=user)
