from __future__ import annotations

import math
import random
from datetime import date, datetime, time as datetime_time, timedelta
from decimal import Decimal

from django.utils import timezone

from django_spire.contrib.seeding import Seeder
from django_spire.metric.domain.statistic.constants import StatisticValueTypeChoices
from django_spire.metric.domain.statistic.models import Statistic, StatisticValue
from django_spire.metric.domain.statistic.querysets import contains_wildcard, reference_matches
from django_spire.metric.domain.statistic.seeding.seeder import VALUE_REFERENCES
from django_spire.metric.visual import models
from django_spire.metric.visual.choices import VisualKindChoices
from django_spire.metric.visual.seeding.constants import VISUAL_REGION_SEEDS, VISUAL_SEEDS

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
    cache_enabled = False
    model_class = models.Visual

    fields_seeds = {
        'id': Seeder.exclude(),
        'name': Seeder.ordered.choice([seed['name'] for seed in VISUAL_SEEDS], wrap=True),
        'description': Seeder.ordered.choice(
            [seed['description'] for seed in VISUAL_SEEDS], wrap=True
        ),
        'kind': Seeder.ordered.choice([seed['kind'] for seed in VISUAL_SEEDS], wrap=True),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def __post_seed_database__(self) -> None:
        visuals_by_name = {visual.name: visual for visual in self.queryset}
        statistic_updates = []

        for index, seed in enumerate(VISUAL_SEEDS):
            visual = visuals_by_name.get(seed['name'])
            if visual is None:
                continue

            statistic = self._statistic_for(seed)
            if statistic is None:
                continue

            if visual.statistic_id != statistic.pk:
                visual.statistic = statistic
                statistic_updates.append(visual)

            self._seed_visual_conditions(visual, statistic)
            self._seed_visual_references(visual, index, seed)
            self._seed_visual_values(visual, statistic)

        models.Visual.objects.bulk_update(statistic_updates, ['statistic'])

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
    def _seed_visual_conditions(visual: models.Visual, statistic: Statistic) -> None:
        target = (
            Decimal(50)
            if statistic.value_type == StatisticValueTypeChoices.PERCENTAGE
            else Decimal(100)
        )
        visual.services.factory.create_default_conditions(target=target, tolerance=Decimal(10))

    @staticmethod
    def _seed_visual_references(visual: models.Visual, index: int, seed: dict) -> None:
        references = (
            []
            if seed['kind'] == VisualKindChoices.PIE
            else [VALUE_REFERENCES[index % len(VALUE_REFERENCES)]]
        )

        for order, reference in enumerate(references):
            visual.references.create(reference=reference, order=order)

    @staticmethod
    def _seed_visual_values(visual: models.Visual, statistic: Statistic) -> None:
        sub_domain = statistic.group.domain.subdomains.active().first()
        if sub_domain is None:
            return

        patterns = list(visual.references.values_list('reference', flat=True))

        references = set()
        for pattern in patterns:
            matched = [
                reference for reference in VALUE_REFERENCES if reference_matches(pattern, reference)
            ]
            if matched:
                references.update(matched)
            elif not contains_wildcard(pattern):
                references.add(pattern)

        references = list(references) if references else VALUE_REFERENCES

        start_date, end_date = visual.services.transformation.date_range()

        existing = set(
            StatisticValue.objects.filter(statistic=statistic, sub_domain=sub_domain).values_list(
                'reference', 'timestamp'
            )
        )

        rows = []
        for reference in references:
            for index in range(VISUAL_VALUE_POINTS):
                timestamp = _visual_timestamp(start_date, end_date, index, VISUAL_VALUE_POINTS)
                if (reference, timestamp) in existing:
                    continue
                rows.append(
                    StatisticValue(
                        statistic=statistic,
                        sub_domain=sub_domain,
                        reference=reference,
                        timestamp=timestamp,
                        value=_visual_value(index, VISUAL_VALUE_POINTS),
                    )
                )

        StatisticValue.objects.bulk_create(rows)


class VisualRegionSeeder(Seeder):
    cache_enabled = False
    model_class = models.VisualRegion

    fields_seeds = {
        'id': Seeder.exclude(),
        'key': Seeder.ordered.choice([seed['key'] for seed in VISUAL_REGION_SEEDS], wrap=True),
        'title': Seeder.ordered.choice([seed['title'] for seed in VISUAL_REGION_SEEDS], wrap=True),
        'is_live_updated': Seeder.ordered.choice(
            [seed['is_live_updated'] for seed in VISUAL_REGION_SEEDS], wrap=True
        ),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def __post_seed_database__(self) -> None:
        visuals_by_name = {visual.name: visual for visual in models.Visual.objects.active()}
        seeds_by_key = {seed['key']: seed for seed in VISUAL_REGION_SEEDS}
        updates = []

        for region in self.queryset:
            seed = seeds_by_key.get(region.key)
            if seed is None:
                continue

            visual = visuals_by_name.get(seed['visual_name'])
            if visual is None or visual.pk == region.visual_id:
                continue

            region.visual = visual
            updates.append(region)

        models.VisualRegion.objects.bulk_update(updates, ['visual'])
