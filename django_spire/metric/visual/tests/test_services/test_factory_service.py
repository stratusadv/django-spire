from __future__ import annotations

from decimal import Decimal

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.choices import VisualConditionOperatorChoices
from django_spire.metric.visual.models import VisualCondition
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_visual,
)


class VisualFactoryServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic, with_conditions=False)

    def test_create_default_conditions(self):
        self.visual.services.factory.create_default_conditions(
            target=Decimal(50), tolerance=Decimal(5)
        )

        conditions = list(self.visual.conditions.order_by('order'))
        assert len(conditions) == 3

        assert conditions[0].state == 'green'
        assert conditions[0].operator == VisualConditionOperatorChoices.GT
        assert conditions[0].target == Decimal(50)

        assert conditions[1].state == 'yellow'
        assert conditions[1].operator == VisualConditionOperatorChoices.BETWEEN
        assert conditions[1].tolerance == Decimal(5)

        assert conditions[2].state == 'red'
        assert conditions[2].operator == VisualConditionOperatorChoices.LT

    def test_create_default_conditions_replaces_existing(self):
        VisualCondition.objects.create(
            visual=self.visual, state='green', operator='gt', target=Decimal(1), order=0
        )

        self.visual.services.factory.create_default_conditions()

        assert self.visual.conditions.count() == 3
