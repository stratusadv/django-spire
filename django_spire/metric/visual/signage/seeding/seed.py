from __future__ import annotations

from django_spire.metric.visual.signage.seeding.seeder import SignageSeeder

signage_seeder = SignageSeeder(count=8)

signage_seeder.seed_database()
