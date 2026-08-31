from __future__ import annotations

from decimal import Decimal

from django.db import IntegrityError
from django.utils import timezone

import pytest

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.history.choices import HistoryEventChoices
from django_spire.metric.domain.statistic.constants import (
    StatisticIntervalChoices,
    StatisticValueTypeChoices,
)
from django_spire.metric.domain.statistic.models import StatisticValue
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
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

    def test_set_deleted_cascades_to_statistics(self):
        statistic = create_test_statistic(group=self.group, name='cascade_statistic')

        self.group.set_deleted()
        self.group.refresh_from_db()
        statistic.refresh_from_db()

        assert self.group.is_deleted is True
        assert statistic.is_deleted is True

    def test_set_deleted_backfills_history_events_for_statistics(self):
        statistic = create_test_statistic(group=self.group, name='history_statistic')

        self.group.set_deleted()

        statistic.refresh_from_db()

        assert statistic.is_deleted is True
        assert statistic.history_events.filter(event=HistoryEventChoices.DELETED).exists()


class StatisticModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_str(self):
        assert str(self.statistic) == self.statistic.name

    def test_default_interval(self):
        assert self.statistic.interval == StatisticIntervalChoices.DAILY

    def test_default_value_type(self):
        assert self.statistic.value_type == StatisticValueTypeChoices.NUMBER

    def test_group_relation(self):
        assert self.statistic.group == self.group

    def test_values_relation(self):
        self.statistic.services.processor.add_value(reference='/home/', sub_domain=self.sub_domain)
        assert self.statistic.values.count() == 1


class StatisticValueModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_str(self):
        statistic_value = StatisticValue.objects.create(
            statistic=self.statistic,
            sub_domain=self.sub_domain,
            reference='/home/',
            value=Decimal(1),
        )
        assert str(statistic_value) == '/home/ (1)'

    def test_raw_append_records_duplicates(self):
        StatisticValue.objects.create(
            statistic=self.statistic, sub_domain=self.sub_domain, reference='/home/'
        )
        StatisticValue.objects.create(
            statistic=self.statistic,
            sub_domain=self.sub_domain,
            reference='/home/',
            value=Decimal(2),
        )
        assert StatisticValue.objects.count() == 2

    def test_distinct_reference_same_time(self):
        StatisticValue.objects.create(
            statistic=self.statistic, sub_domain=self.sub_domain, reference='/home/'
        )
        StatisticValue.objects.create(
            statistic=self.statistic, sub_domain=self.sub_domain, reference='/dashboard/'
        )
        assert StatisticValue.objects.count() == 2

    def test_timestamp_defaults_to_now(self):
        statistic_value = StatisticValue.objects.create(
            statistic=self.statistic, sub_domain=self.sub_domain, reference='/home/'
        )
        assert statistic_value.timestamp.tzinfo is not None
        elapsed = (timezone.now() - statistic_value.timestamp).total_seconds()
        assert 0 <= elapsed < 5

    def test_sub_domain_required(self):
        with pytest.raises(IntegrityError):
            StatisticValue.objects.create(statistic=self.statistic, reference='/home/')

    def test_sub_domain_relation(self):
        statistic_value = StatisticValue.objects.create(
            statistic=self.statistic, sub_domain=self.sub_domain, reference='/home/'
        )
        assert self.sub_domain.values.count() == 1
        assert statistic_value in self.sub_domain.values.all()

    def test_indexes_present(self):
        index_names = {index.name for index in StatisticValue._meta.indexes}
        assert {'ix_statistic_timestamp', 'ix_statistic_subdomain_ts'} <= index_names
