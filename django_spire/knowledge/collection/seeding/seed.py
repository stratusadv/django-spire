from __future__ import annotations

from django_spire.knowledge.collection.seeding.seeder import CollectionSeeder

parent_collections = CollectionSeeder.seed_database(count=5)
child_collections = CollectionSeeder.seed_child_collections(count=15)

from django_spire.knowledge.entry.seeding.seed import *
