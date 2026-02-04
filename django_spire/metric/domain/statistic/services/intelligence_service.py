from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.metric.domain.statistic.models import Statistic


class StatisticIntelligenceService(BaseDjangoModelService['Statistic']):
    obj: Statistic
