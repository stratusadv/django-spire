from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

from django_spire.history.choices import HistoryEventChoices
from django_spire.history.models import HistoryEvent

if TYPE_CHECKING:
    from django.db.models import QuerySet


def soft_delete_queryset(queryset: QuerySet) -> list[int]:
    affected = list(queryset.filter(is_deleted=False).values_list('pk', flat=True))

    if affected:
        queryset.filter(pk__in=affected).update(is_deleted=True)

        content_type = ContentType.objects.get_for_model(queryset.model)
        HistoryEvent.objects.bulk_create(
            HistoryEvent(content_type=content_type, object_id=pk, event=HistoryEventChoices.DELETED)
            for pk in affected
        )

    return affected
