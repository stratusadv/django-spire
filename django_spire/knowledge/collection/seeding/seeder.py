from __future__ import annotations

from django_spire.contrib.seeding import Seeder
from django_spire.knowledge.collection import models


class CollectionSeeder(Seeder):
    model_class = models.Collection

    fields_seeds = {
        'id': Seeder.exclude(),
        'parent_id': Seeder.exclude(),
        'name': Seeder.llm(
            str, 'A name for a knowledge base collection, e.g. a department, team, or topic area.'
        ),
        'description': Seeder.llm(
            str, 'Short description of what documents this knowledge base collection holds.'
        ),
    }

    def __post_seed_database__(self) -> None:
        self._correct_order()

    @classmethod
    def _correct_order(cls) -> None:
        parents = models.Collection.objects.filter(child__isnull=False).distinct()

        for parent_collection in parents:
            children = parent_collection.children.all()

            for idx, child_collection in enumerate(children):
                child_collection.order = idx

            models.Collection.objects.bulk_update(children, ['order'])


class ChildCollectionSeeder(Seeder):
    model_class = models.Collection

    fields_seeds = {
        'id': Seeder.exclude(),
        'parent_id': Seeder.model.random_queryset_foreign_key(
            models.Collection.objects.parentless()
        ),
        'name': Seeder.llm(
            str, 'A name for a child knowledge base collection, e.g. a topic within a department.'
        ),
        'description': Seeder.llm(
            str, 'Short description of what documents this child knowledge base collection holds.'
        ),
    }

    def __post_seed_database__(self) -> None:
        CollectionSeeder._correct_order()


class GrandchildCollectionSeeder(Seeder):
    model_class = models.Collection

    fields_seeds = {
        'id': Seeder.exclude(),
        'parent_id': Seeder.model.random_queryset_foreign_key(
            models.Collection.objects.filter(parent__isnull=False)
        ),
        'name': Seeder.llm(
            str, 'A name for a nested knowledge base collection, e.g. a sub-topic within a child.'
        ),
        'description': Seeder.llm(
            str, 'Short description of what documents this nested knowledge base collection holds.'
        ),
    }

    def __post_seed_database__(self) -> None:
        CollectionSeeder._correct_order()
