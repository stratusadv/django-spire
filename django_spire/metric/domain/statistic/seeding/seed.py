from __future__ import annotations

from django_spire.metric.domain.statistic.seeding.seeder import (
    StatisticGroupSeeder,
    StatisticSeeder,
    seed_statistic_values,
)

statistic_group_seeder = StatisticGroupSeeder(count=5)

statistic_group_seeder.seed_database()

statistic_seeder = StatisticSeeder(count=10)

statistic_seeder.seed_database()

seed_statistic_values(count=1000)
