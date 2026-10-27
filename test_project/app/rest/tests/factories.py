from __future__ import annotations

from typing import Any
from uuid import uuid4

from test_project.app.rest.models import Pirate


def create_test_pirate(**kwargs: Any) -> Pirate:
    defaults = {
        'first_name': 'Anne',
        'last_name': 'Bonny',
        'email': 'anne.bonny@example.com',
        'username': f'pirate-{uuid4().hex}',
    }

    defaults.update(kwargs)

    return Pirate.objects.create(**defaults)
