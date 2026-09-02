from __future__ import annotations

from django_spire.metric.visual.presentation.seeding.constants import PRESENTATION_SEEDS
from django_spire.metric.visual.presentation.seeding.seeder import PresentationSeeder

presentation_seeder = PresentationSeeder(count=len(PRESENTATION_SEEDS))

presentation_seeder.seed_database()
