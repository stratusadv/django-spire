from __future__ import annotations

from django_spire.api.seeding.seeder import ApiAccessSeeder


ApiAccessSeeder.seed_database(count=5)
ApiAccessSeeder.update_hashed_keys()