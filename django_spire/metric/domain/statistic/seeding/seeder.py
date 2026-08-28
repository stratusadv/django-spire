from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from django.utils import timezone

from django_spire.contrib.seeding import Seeder
from django_spire.metric.domain.models import Domain
from django_spire.metric.domain.seeding.constants import (
    GROUP_SEEDS,
    STATISTIC_KEYS,
    STATISTIC_SEEDS,
)
from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup, StatisticValue

if TYPE_CHECKING:
    from django.db.models import QuerySet


class StatisticGroupSeeder(Seeder):
    model_class = StatisticGroup

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'domain_id': Seeder.model.ordered_queryset_foreign_key(Domain.objects.all(), wrap=True),
        'name': Seeder.ordered.choice([seed['name'] for seed in GROUP_SEEDS], wrap=True),
        'description': Seeder.ordered.choice(
            [seed['description'] for seed in GROUP_SEEDS], wrap=True
        ),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def seed_database(self, count: int | None = None) -> QuerySet:
        self.seed(count)

        effective_count = self._count if count is None else count

        if effective_count > len(GROUP_SEEDS):
            return super().seed_database(count)

        domains = list(Domain.objects.all().order_by('pk'))
        model_objects = []
        for index, fields in enumerate(self.to_list_of_dicts()):
            domain = domains[index % len(domains)]
            obj, _ = StatisticGroup.objects.update_or_create(
                domain=domain,
                name=fields['name'],
                defaults={
                    'description': fields['description'],
                    'created_datetime': fields['created_datetime'],
                    'is_active': fields['is_active'],
                    'is_deleted': fields['is_deleted'],
                },
            )
            model_objects.append(obj)

        self._model_object_ids = [model_object.id for model_object in model_objects]
        return self.queryset


class StatisticSeeder(Seeder):
    model_class = Statistic

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'group_id': Seeder.model.ordered_queryset_foreign_key(
            StatisticGroup.objects.all(), wrap=True
        ),
        'name': Seeder.ordered.choice([seed['name'] for seed in STATISTIC_SEEDS], wrap=True),
        'interval': Seeder.model.random_field_choice(StatisticIntervalChoices),
        'value_type': Seeder.ordered.choice(
            [seed['value_type'] for seed in STATISTIC_SEEDS], wrap=True
        ),
        'key': Seeder.ordered.choice(STATISTIC_KEYS, wrap=True),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def seed_database(self, count: int | None = None) -> QuerySet:
        self.seed(count)

        groups = list(StatisticGroup.objects.all().order_by('pk'))
        model_objects = []
        for index, fields in enumerate(self.to_list_of_dicts()):
            group = groups[index % len(groups)]
            obj, _ = Statistic.objects.update_or_create(
                key=fields['key'],
                defaults={
                    'group': group,
                    'name': fields['name'],
                    'interval': fields['interval'],
                    'value_type': fields['value_type'],
                    'created_datetime': fields['created_datetime'],
                    'is_active': fields['is_active'],
                    'is_deleted': fields['is_deleted'],
                },
            )
            model_objects.append(obj)

        self._model_object_ids = [model_object.id for model_object in model_objects]
        return self.queryset


VALUE_REFERENCES = [
    'django_spire:metric:domain:statistic:page:list',
    'django_spire:metric:domain:statistic:page:detail',
    'django_spire:metric:domain:page:list',
    'django_spire:metric:domain:page:detail',
]


def seed_statistic_values(count: int = 1000) -> None:
    options = []
    for statistic in (
        Statistic.objects.active()
        .not_deleted()
        .select_related('group__domain')
        .order_by('pk')
    ):
        sub_domains = list(statistic.group.domain.subdomains.active().order_by('pk'))
        if sub_domains:
            options.append((statistic, sub_domains))

    if not options:
        return

    options = [
        (statistic, sub_domains)
        for statistic, sub_domains in options
        if not statistic.values.exists()
    ]

    if not options:
        return

    now = timezone.now()
    rows = []

    for index in range(count):
        statistic, sub_domains = options[index % len(options)]
        rows.append(
            StatisticValue(
                statistic=statistic,
                sub_domain=sub_domains[index % len(sub_domains)],
                reference=VALUE_REFERENCES[index % len(VALUE_REFERENCES)],
                timestamp=now - timedelta(minutes=(index * 137) % (30 * 24 * 60)),
                value=(index % 100) + 1,
            )
        )

    StatisticValue.objects.bulk_create(rows, batch_size=500)
