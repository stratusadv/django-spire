from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet


class OrderingQuerySet(HistoryQuerySet):
    pass
