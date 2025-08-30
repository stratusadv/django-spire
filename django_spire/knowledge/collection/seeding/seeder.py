from __future__ import annotations

from django_spire.knowledge.collection import models

from django_spire.contrib.seeding import DjangoModelSeeder


class CollectionSeeder(DjangoModelSeeder):
    model_class = models.Collection
    # cache_name = 'collection_seeder'
    fields = {
        'id': 'exclude',
        'parent': 'exclude',
        'name': (
            'llm',
            'A name for a collection of documents. Make it fun and give it a theme'
        ),
        'description': (
            'llm',
            'Short description on the what the documents are about, keep it related to the name.'
        ),
    }

    @classmethod
    def seed_child_collections(cls, count: int = 1) -> list[models.Collection]:
        return cls.seed_database(
            count=count,
            fields=cls.fields | {
                'parent_id': ('custom', 'fk_random', {'model_class': models.Collection})
            },
        )
