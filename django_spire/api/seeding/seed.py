from __future__ import annotations

from django_spire.api.seeding.seeder import ApiAccessSeeder


api_seeder = ApiAccessSeeder(count=5)

api_seeder.seed_database()
