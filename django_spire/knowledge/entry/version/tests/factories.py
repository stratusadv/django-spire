from __future__ import annotations

import random
import string

from django_spire.auth.user.tests.factories import create_user
from django_spire.knowledge.entry.tests.factories import create_test_entry
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices
from django_spire.knowledge.entry.version.models import EntryVersion


def random_string(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def create_test_entry_version(**kwargs) -> EntryVersion:
    data = {
        'entry': kwargs.pop('entry', None) or create_test_entry(),
        'author': kwargs.pop('author', None) or create_user(username=f'author_{random_string(8)}'),
        'status': EntryVersionStatusChoices.DRAFT,
    }
    data.update(kwargs)
    return EntryVersion.objects.create(**data)
