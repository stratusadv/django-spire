from __future__ import annotations

from django_spire.metric.visual.seeding.constants import VISUAL_REGION_SEEDS, VISUAL_SEEDS
from django_spire.metric.visual.seeding.seeder import VisualRegionSeeder, VisualSeeder


visual_seeder = VisualSeeder(count=len(VISUAL_SEEDS))

visual_seeder.seed_database()

visual_region_seeder = VisualRegionSeeder(count=len(VISUAL_REGION_SEEDS))

visual_region_seeder.seed_database()
