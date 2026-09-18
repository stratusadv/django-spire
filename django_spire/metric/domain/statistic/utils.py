from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def detach_visuals_from_statistics(statistic_ids: Iterable[int]) -> None:
    from django_spire.metric.visual.models import Visual

    Visual.objects.filter(statistic_id__in=list(statistic_ids), is_deleted=False).update(
        statistic_id=None
    )
