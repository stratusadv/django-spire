from __future__ import annotations

from django.utils import timezone

from test_project.apps.model_and_service.models import Adult, Kid


def create_adult(**kwargs) -> Adult:
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'description': 'This is a sample description used for testing.',
        'personality_type': 'ext',
        'email': 'john.doe@example.com',
        'favorite_number': 42,
        'anniversary_datetime': timezone.make_aware(timezone.datetime(2025, 6, 21, 10, 0, 0)),
        'birth_date': '1990-01-01',
        'weight_lbs': 175.5,
        'bed_time': '20:00',
        'likes_to_party': True
    }
    data.update(kwargs)
    return Adult.objects.create(**data)


def create_kid(**kwargs) -> Kid:
    parent = kwargs.pop('parent', create_adult())
    data = {
        'parent': parent,
        'first_name': 'Junior',
        'last_name': 'Doe'
    }
    data.update(kwargs)
    return Kid.objects.create(**data)
