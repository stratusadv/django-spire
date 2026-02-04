from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.seeding import DjangoModelSeeder

from django_spire.metric.domain import models

if TYPE_CHECKING:
    from typing import ClassVar


class DomainSeeder(DjangoModelSeeder):
    """https://django-spire.stratusadv.com/app_guides/seeding/overview/"""

    model_class = models.Domain
    default_to = 'faker'

    fields: ClassVar = {
        'id': 'exclude',
        'created_datetime': 'exclude',
        'is_active': True,
        'is_deleted': False,
        # 'name': ('faker', 'company'),
        # 'status': ('faker'),
    }
