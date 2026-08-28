from __future__ import annotations

import math
import random
from datetime import date, datetime, time as datetime_time, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django.utils import timezone

from django_spire.contrib.seeding import Seeder
from django_spire.metric.domain.statistic.models import Statistic, StatisticValue
from django_spire.metric.domain.statistic.seeding.seeder import VALUE_REFERENCES
from django_spire.metric.visual import models
from django_spire.metric.visual.choices import VisualKindChoices
from django_spire.metric.visual.seeding.constants import VISUAL_SEEDS

if TYPE_CHECKING:
    from typing import ClassVar

    from django.db.models import QuerySet

VISUAL_VALUE_POINTS = 30


def _visual_value(index: int, points: int) -> Decimal:
    progress = (index + 1) / points
    wave = math.sin(progress * math.tau * 2 + math.pi)
    return Decimal(str(round(3 + 2 * wave + random.uniform(-0.5, 0.5), 2)))


def _visual_timestamp(start_date: date, end_date: date, index: int, points: int) -> datetime:
    current_tz = timezone.get_current_timezone()
    start_dt = datetime.combine(start_date, datetime_time.min, tzinfo=current_tz)
    end_dt = datetime.combine(end_date, datetime_time.max, tzinfo=current_tz)
    total_seconds = int((end_dt - start_dt).total_seconds())
    offset = total_seconds * index // max(points - 1, 1)
    return start_dt + timedelta(seconds=offset)


class VisualSeeder(Seeder):
    model_class = models.Visual

    fields_seeds: ClassVar = {}

    def seed_database(self, count: int | None = None) -> QuerySet:  # noqa: ARG002
        model_objects = []

        for index, seed in enumerate(VISUAL_SEEDS):
            statistic = self._statistic_for(seed)
            if statistic is None:
                continue

            visual_class = models.Visual.kind_model(seed['kind'])
            reference = (
                ''
                if seed['kind'] == VisualKindChoices.PIE
                else VALUE_REFERENCES[index % len(VALUE_REFERENCES)]
            )

            visual, _ = visual_class.objects.get_or_create(
                name=seed['name'],
                defaults={
                    'description': seed['description'],
                    'statistic': statistic,
                    'reference': reference,
                    'date': timezone.localdate(),
                    'is_active': True,
                    'is_deleted': False,
                },
            )

            if not visual.conditions.exists():
                visual.services.factory.create_default_conditions(
                    target=Decimal(100), tolerance=Decimal(10)
                )

            self._seed_visual_values(visual)

            model_objects.append(visual)

        self._model_object_ids = [model_object.id for model_object in model_objects]

        return self.queryset

    @staticmethod
    def _statistic_for(seed: dict) -> Statistic | None:
        queryset = Statistic.objects.active().not_deleted()
        statistic_name = seed.get('statistic')
        if statistic_name:
            statistic = queryset.filter(name=statistic_name).first()
            if statistic is not None:
                return statistic
        return queryset.first()

    @staticmethod
    def _seed_visual_values(visual: models.Visual) -> None:
        sub_domain = visual.statistic.group.domain.subdomains.active().first()
        if sub_domain is None:
            return

        references = [visual.reference] if visual.reference else VALUE_REFERENCES

        start_date, end_date = visual.services.transformation.date_range()

        existing = set(
            StatisticValue.objects.filter(
                statistic=visual.statistic, sub_domain=sub_domain
            ).values_list('reference', 'timestamp')
        )

        rows = []
        for reference in references:
            for index in range(VISUAL_VALUE_POINTS):
                timestamp = _visual_timestamp(start_date, end_date, index, VISUAL_VALUE_POINTS)
                if (reference, timestamp) in existing:
                    continue
                rows.append(
                    StatisticValue(
                        statistic=visual.statistic,
                        sub_domain=sub_domain,
                        reference=reference,
                        timestamp=timestamp,
                        value=_visual_value(index, VISUAL_VALUE_POINTS),
                    )
                )

        StatisticValue.objects.bulk_create(rows)
