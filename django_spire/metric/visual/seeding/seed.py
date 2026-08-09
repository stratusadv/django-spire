from __future__ import annotations

from django_spire.metric.visual.seeding.seeder import VisualSeeder


visual_seeder = VisualSeeder(count=10)

visual_seeder.seed_database()
