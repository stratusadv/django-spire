from __future__ import annotations

from django_spire.metric.visual.seeding.seeder import VisualRegionSeeder, VisualSeeder


visual_seeder = VisualSeeder(count=10)

visual_seeder.seed_database()

visual_region_seeder = VisualRegionSeeder()

visual_region_seeder.seed_database()
