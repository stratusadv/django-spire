from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.seeding import DjangoModelSeeder

from test_project.apps.lazy_tabs import models

if TYPE_CHECKING:
    from typing import ClassVar


class LazyTabsSeeder(DjangoModelSeeder):
    model_class = models.LazyTabs
    default_to = 'faker'

    fields: ClassVar = {
        'id': 'exclude',
        'created_datetime': ('custom', 'date_time_between', {'start_date': '-30d', 'end_date': 'now'}),
        'is_active': True,
        'is_deleted': False,
        'name': ('faker', 'catch_phrase'),
        'description': ('faker', 'paragraph'),
    }
