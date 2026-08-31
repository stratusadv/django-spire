from __future__ import annotations

from decimal import Decimal

from django.db import IntegrityError

import pytest

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.models import SubDomain
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_statistic,
    create_test_statistic_group,
)
from django_spire.metric.domain.tests.factories import create_test_domain, create_test_subdomain


class DomainModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()

    def test_str(self):
        assert str(self.domain) == str(self.domain.name)

    def test_set_deleted_cascades_to_groups_and_statistics(self):
        sub_domain = create_test_subdomain(domain=self.domain)
        group = create_test_statistic_group(domain=self.domain)
        statistic = create_test_statistic(group=group)
        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(1), sub_domain=sub_domain
        )

        self.domain.set_deleted()

        self.domain.refresh_from_db()
        group.refresh_from_db()
        statistic.refresh_from_db()

        assert self.domain.is_deleted is True
        assert group.is_deleted is True
        assert statistic.is_deleted is True
        assert statistic.values.count() == 1
        assert statistic.services.transformation.value_queryset().count() == 0


class SubDomainModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.subdomain = create_test_subdomain(domain=self.domain)

    def test_str(self):
        assert str(self.subdomain) == str(self.subdomain.name)

    def test_key_assigned_on_create(self):
        assert self.subdomain.key is not None

    def test_key_slugs_from_name_on_create(self):
        subdomain = create_test_subdomain(domain=self.domain, name='Website Traffic')
        assert subdomain.key == 'website-traffic'

    def test_key_not_regenerated_on_update(self):
        key = self.subdomain.key
        self.subdomain.name = 'Renamed Subdomain'
        self.subdomain.save()
        self.subdomain.refresh_from_db()
        assert self.subdomain.key == key
        assert self.subdomain.name == 'Renamed Subdomain'

    def test_key_collision_appends_suffix(self):
        create_test_subdomain(domain=self.domain, name='Clients')
        second = create_test_subdomain(domain=self.domain, name='Clients')
        assert second.key == 'clients-2'

    def test_key_is_unique(self):
        duplicate = SubDomain(domain=self.domain, name='duplicate', key=self.subdomain.key)
        with pytest.raises(IntegrityError):
            duplicate.save()
