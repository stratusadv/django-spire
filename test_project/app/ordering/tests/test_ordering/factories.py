from test_project.app.ordering.models import Duck


def create_test_duck(**kwargs) -> Duck:
    default = {
        'order': 0,
        'name': 'Sir Duckington'
    }

    default.update(kwargs)

    return Duck.objects.create(**default)