from __future__ import annotations

from django_spire.metric.visual.signage.seeding.constants import SIGNAGE_SEEDS
from django_spire.metric.visual.signage.seeding.seeder import SignageSeeder

signage_seeder = SignageSeeder(count=len(SIGNAGE_SEEDS))

signage_seeder.seed_database()
