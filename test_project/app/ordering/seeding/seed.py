from __future__ import annotations

from test_project.app.ordering.seeding.seeder import DuckSeeder


duck_seeder = DuckSeeder(count=20)

duck_seeder.seed_database()
