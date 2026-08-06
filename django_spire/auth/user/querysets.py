from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import UserManager

from django_spire.core.querysets import SearchQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.auth.user.models import AuthUser


class AuthUserQuerySet(HistoryQuerySet, SearchQuerySetMixin):
    def bulk_filter(self, filter_data: dict) -> QuerySet[AuthUser]:
        queryset = self

        search = filter_data.get('search', '')
        if search:
            queryset = queryset.search(search)

        return queryset


class AuthUserManager(UserManager.from_queryset(AuthUserQuerySet)):
    pass
