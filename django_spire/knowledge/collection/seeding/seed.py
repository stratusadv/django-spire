from __future__ import annotations

from django_spire.knowledge.collection.seeding.seeder import (
    ChildCollectionSeeder,
    CollectionSeeder,
    GrandchildCollectionSeeder,
)


parent_collection_seeder = CollectionSeeder(count=1)
parent_collection_seeder.seed_database()

child_collection_seeder = ChildCollectionSeeder(count=4)
child_collection_seeder.seed_database()

grandchild_collection_seeder = GrandchildCollectionSeeder(count=3)
grandchild_collection_seeder.seed_database()

from django_spire.knowledge.entry.seeding.seed import *  # noqa: E402, F403
