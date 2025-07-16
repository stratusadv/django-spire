from django_spire.knowledge.collection.models import Collection


def create_test_collection(**kwargs) -> Collection:
    data = {
        'parent': None,
        'name': 'Video Game Cheat Codes',
        'description': 'A collection of video game cheat codes.'
    }
    data.update(kwargs)
    return Collection.objects.create(**data)
