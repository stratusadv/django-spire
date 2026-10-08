from __future__ import annotations

from typing import Any

from test_project.app.ordering.models import Duck


def create_test_duck(**kwargs: Any) -> Duck:
    defaults = {
        'name': 'Mallard',
        'color': '#336699',
        'order': 0,
    }

    defaults.update(kwargs)

    return Duck.objects.create(**defaults)
