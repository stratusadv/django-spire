from __future__ import annotations

from django_spire.metric.domain.statistic.seeding.seeder import (
    StatisticGroupSeeder,
    StatisticSeeder,
    StatisticValueSeeder,
)


statistic_group_seeder = StatisticGroupSeeder(count=5)

statistic_group_seeder.seed_database()


statistic_seeder = StatisticSeeder(count=10)

statistic_seeder.seed_database()


statistic_value_seeder = StatisticValueSeeder(count=25)

statistic_value_seeder.seed_database()
