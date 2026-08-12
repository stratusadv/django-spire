from __future__ import annotations

from django_spire.knowledge.entry.seeding.seeder import EntrySeeder


entry_seeder = EntrySeeder(count=15)
entry_seeder.seed_database()
