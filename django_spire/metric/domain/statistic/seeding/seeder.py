from datetime import timedelta

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


class StatisticSeeder(Seeder):
    model_class = Statistic

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'group_id': Seeder.model.ordered_queryset_foreign_key(
            StatisticGroup.objects.all(), wrap=True
        ),
        'name': Seeder.ordered.choice(STATISTIC_SEEDS, wrap=True),
        'interval': Seeder.model.random_field_choice(StatisticIntervalChoices),
        'key': Seeder.ordered.choice(STATISTIC_KEYS, wrap=True),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }


VALUE_REFERENCES = ['/home/', '/dashboard/', '/contact/', '/pricing/']


def seed_statistic_values(count: int = 1000) -> None:
    options = []
    for statistic in (
        Statistic.objects.active().not_deleted().select_related('group__domain').order_by('pk')
    ):
        sub_domains = list(statistic.group.domain.subdomains.active().order_by('pk'))
        if sub_domains:
            options.append((statistic, sub_domains))

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
