from __future__ import annotations

from django_spire.auth.group.models import AuthGroup
from django_spire.knowledge.collection.models import Collection, CollectionGroup


def create_test_auth_group(**kwargs) -> AuthGroup:
    data = {
        'name': 'Test Group',
    }
    data.update(kwargs)
    return AuthGroup.objects.create(**data)


def create_test_collection(**kwargs) -> Collection:
    data = {
        'parent': None,
        'name': 'Video Game Cheat Codes',
        'description': 'A collection of video game cheat codes.',
        'is_deleted': False,
        'is_active': True
    }
    data.update(kwargs)
    return Collection.objects.create(**data)


def create_test_collection_group(
    collection: Collection | None = None,
    auth_group: AuthGroup | None = None,
    **kwargs
) -> CollectionGroup:
    if collection is None:
        collection = create_test_collection()
    if auth_group is None:
        auth_group = create_test_auth_group()

    data = {
        'collection': collection,
        'auth_group': auth_group,
    }
    data.update(kwargs)
    return CollectionGroup.objects.create(**data)
