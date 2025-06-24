from test_project.apps.test_model.models import TestModel, TestModelChild


def create_test_model(**kwargs):
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'description': 'This is a sample description used for testing.',
        'personality_type': 'ext',
        'email': 'john.doe@example.com',
        'favorite_number': 42,
        'anniversary_datetime': '2025-06-21 10:00:00',
        'birth_date': '1990-01-01',
        'weight_lbs': 175.5,
        'bed_time': '20:00',
        'likes_to_party': True
    }
    data.update(kwargs)
    return TestModel.objects.create(**data)


def create_test_model_child(**kwargs):
    parent = kwargs.pop('parent', create_test_model())
    data = {
        'parent': parent,
        'first_name': 'Junior',
        'last_name': 'Doe'
    }
    data.update(kwargs)
    return TestModelChild.objects.create(**data)
