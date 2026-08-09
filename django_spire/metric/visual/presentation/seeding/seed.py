from __future__ import annotations

from django_spire.metric.visual.presentation.seeding.seeder import PresentationSeeder

presentation_seeder = PresentationSeeder(count=5)

presentation_seeder.seed_database()
