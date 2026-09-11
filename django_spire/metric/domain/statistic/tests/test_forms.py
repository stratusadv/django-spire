from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.forms import StatisticForm, StatisticGroupForm
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic_group,
)


class StatisticGroupFormTestCase(BaseTestCase):
    def test_deleted_domain_is_not_selectable(self):
        domain = create_test_domain(name='gone')
        domain.set_deleted()
        create_test_domain(name='live')

        form = StatisticGroupForm()

        domain_pks = {pk for pk, _ in form.fields['domain'].choices}
        assert domain.pk not in domain_pks

    def test_live_domain_is_selectable(self):
        domain = create_test_domain(name='live')

        form = StatisticGroupForm()

        domain_pks = {pk for pk, _ in form.fields['domain'].choices}
        assert domain.pk in domain_pks


class StatisticFormTestCase(BaseTestCase):
    def test_deleted_group_is_not_selectable(self):
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain, name='gone')
        group.set_deleted()
        create_test_statistic_group(domain=domain, name='live')

        form = StatisticForm()

        group_pks = {pk for pk, _ in form.fields['group'].choices}
        assert group.pk not in group_pks

    def test_live_group_is_selectable(self):
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain, name='live')

        form = StatisticForm()

        group_pks = {pk for pk, _ in form.fields['group'].choices}
        assert group.pk in group_pks
