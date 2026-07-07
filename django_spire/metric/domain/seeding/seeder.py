from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.seeding import DjangoModelSeeder
from django_spire.metric.domain import models

if TYPE_CHECKING:
    from typing import ClassVar


class DomainSeeder(DjangoModelSeeder):
    """https://django-spire.stratusadv.com/app_guides/seeding/overview/"""

    model_class = models.Domain
    cache_name = 'domain_seeder'

    fields = {
        'id': 'exclude',
        'created_datetime': 'exclude',
        'name': ('llm', 'A name for a metrics domain.'),
        'description': (
            'llm',
            'Domain description. Put a random description here for metric domain.',
        ),
        'sub_domain_description': (
            'llm',
            'Sub Domain description. Put a random description here for metric sub_domain like clients.',
        ),
    }


class SubDomainSeeder(DjangoModelSeeder):
    model_class = models.SubDomain
    cache_name = 'subdomain_seeder'

    fields = {
        'id': 'exclude',
        'created_datetime': 'exclude',
        'domain_id': ('custom', 'fk_random', {'model_class': models.Domain}),
        'name': ('llm', 'A name for a sub_domain'),
        'description': (
            'llm',
            'Sub Domain description. Put a random description here for metric sub_domain like clients or departments.',
        ),
    }
