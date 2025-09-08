from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.models import Entry


def create_test_entry(**kwargs) -> Entry:
    data = {
        'collection': create_test_collection(),
        'name': 'Video Game Cheat Codes',
        'is_deleted': False,
        'is_active': True
    }
    data.update(kwargs)
    return Entry.objects.create(**data)
