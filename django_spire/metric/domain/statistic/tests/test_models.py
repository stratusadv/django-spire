from __future__ import annotations

from decimal import Decimal

from django.db import IntegrityError

import pytest

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices
from django_spire.metric.domain.statistic.models import StatisticValue
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
)


class StatisticGroupModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.group = create_test_statistic_group(domain=self.domain)

    def test_str(self):
        assert str(self.group) == self.group.name

    def test_subdomains_qs(self):
        assert list(self.group.subdomains_qs()) == list(self.domain.subdomains.active())

    def test_subdomains_qs_with_subdomain(self):
        self.domain.subdomains.create(name='sub')
        assert self.group.subdomains_qs().count() == 1

    def test_domain_relation(self):
        self.domain.statistic_groups.create(name='second group')
        assert self.domain.statistic_groups.count() == 2


class StatisticModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_str(self):
        assert str(self.statistic) == self.statistic.name

    def test_default_interval(self):
        assert self.statistic.interval == StatisticIntervalChoices.DAILY

    def test_group_relation(self):
        assert self.statistic.group == self.group

    def test_values_relation(self):
        self.statistic.services.processor.add_value(reference='/home/')
        assert self.statistic.values.count() == 1


class StatisticValueModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_str(self):
        statistic_value = StatisticValue.objects.create(
            statistic=self.statistic, reference='/home/', value=Decimal(1)
        )
        assert str(statistic_value) == '/home/ (1)'

    def test_unique_per_reference_and_date(self):
        StatisticValue.objects.create(statistic=self.statistic, reference='/home/')
        with pytest.raises(IntegrityError):
            StatisticValue.objects.create(statistic=self.statistic, reference='/home/')

    def test_distinct_reference_same_date(self):
        StatisticValue.objects.create(statistic=self.statistic, reference='/home/')
        StatisticValue.objects.create(statistic=self.statistic, reference='/dashboard/')
        assert StatisticValue.objects.count() == 2
