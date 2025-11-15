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
    def _correct_order(
        cls,
        child_collections: list[models.Collection]
    ) -> list[models.Collection]:
        parent_collections = cls.model_class.objects.parentless()

        for parent_collection in parent_collections:
            children = parent_collection.children.all()
            for idx, child_collection in enumerate(children):
                child_collection.order = idx

            cls.model_class.objects.bulk_update(children, ['order'])

        return child_collections

    @classmethod
    def seed_child_collections(cls, count: int = 1) -> list[models.Collection]:
        return cls._correct_order(
            cls.seed_database(
                count=count,
                fields=cls.fields | {
                    'parent_id': ('custom', 'fk_random', {'model_class': models.Collection})
                },
            )
        )
