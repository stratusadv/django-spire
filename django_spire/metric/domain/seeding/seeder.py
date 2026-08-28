from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.seeding import Seeder
from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.seeding.constants import (
    DOMAIN_SEEDS,
    SUB_DOMAIN_KEYS,
    SUBDOMAIN_SEEDS,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet


class DomainSeeder(Seeder):
    model_class = Domain

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'name': Seeder.ordered.choice([seed['name'] for seed in DOMAIN_SEEDS], wrap=True),
        'description': Seeder.ordered.choice(
            [seed['description'] for seed in DOMAIN_SEEDS], wrap=True
        ),
        'sub_domain_name': Seeder.ordered.choice(
            [seed['sub_domain_name'] for seed in DOMAIN_SEEDS], wrap=True
        ),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def seed_database(self, count: int | None = None) -> QuerySet:
        self.seed(count)

        effective_count = self._count if count is None else count

        if effective_count > len(DOMAIN_SEEDS):
            return super().seed_database(count)

        model_objects = []
        for fields in self.to_list_of_dicts():
            obj, _ = Domain.objects.update_or_create(
                name=fields['name'],
                defaults={
                    'description': fields['description'],
                    'sub_domain_name': fields['sub_domain_name'],
                    'created_datetime': fields['created_datetime'],
                    'is_active': fields['is_active'],
                    'is_deleted': fields['is_deleted'],
                },
            )
            model_objects.append(obj)

        self._model_object_ids = [model_object.id for model_object in model_objects]
        return self.queryset


class SubDomainSeeder(Seeder):
    model_class = SubDomain

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'domain_id': Seeder.model.ordered_queryset_foreign_key(Domain.objects.active(), wrap=True),
        'name': Seeder.ordered.choice([seed['name'] for seed in SUBDOMAIN_SEEDS], wrap=True),
        'description': Seeder.ordered.choice(
            [seed['description'] for seed in SUBDOMAIN_SEEDS], wrap=True
        ),
        'key': Seeder.ordered.choice(SUB_DOMAIN_KEYS, wrap=True),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def seed_database(self, count: int | None = None) -> QuerySet:
        self.seed(count)

        domains = {domain.name: domain for domain in Domain.objects.active()}
        if not domains:
            return self.queryset

        model_objects = []
        for index, fields in enumerate(self.to_list_of_dicts()):
            seed = SUBDOMAIN_SEEDS[index % len(SUBDOMAIN_SEEDS)]
            domain = domains.get(seed['domain'])
            if domain is None:
                continue

            obj, _ = SubDomain.objects.update_or_create(
                key=fields['key'],
                defaults={
                    'domain': domain,
                    'name': fields['name'],
                    'description': fields['description'],
                    'created_datetime': fields['created_datetime'],
                    'is_active': fields['is_active'],
                    'is_deleted': fields['is_deleted'],
                },
            )
            model_objects.append(obj)

        self._model_object_ids = [model_object.id for model_object in model_objects]
        return self.queryset
