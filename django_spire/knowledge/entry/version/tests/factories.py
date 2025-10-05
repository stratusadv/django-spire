from __future__ import annotations

from keyring.testing.util import random_string

from django_spire.auth.user.tests.factories import create_user
from django_spire.knowledge.entry.tests.factories import create_test_entry
from django_spire.knowledge.entry.version.models import EntryVersion


def create_test_entry_version(**kwargs) -> EntryVersion:
    data = {
        'entry': create_test_entry(),
        'author': create_user(username=random_string(k=10)),
        'is_deleted': False,
        'is_active': True
    }
    data.update(kwargs)
    return EntryVersion.objects.create(**data)
