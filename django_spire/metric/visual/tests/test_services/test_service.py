from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.models import VisualCondition, VisualReference
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_visual,
)


class VisualReferenceServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic)

        self.visual.references.create(reference='/a/', order=0)

    def _add_reference(self, **kwargs) -> VisualReference:
        reference = VisualReference(visual=self.visual)
        reference.services.save_model_obj(reference='/new/', **kwargs)
        reference.refresh_from_db()
        return reference

    def test_create_keeps_free_order(self):
        reference = self._add_reference(order=1)

        assert reference.order == 1

    def test_create_assigns_next_order_on_collision(self):
        reference = self._add_reference(order=0)

        assert reference.order == 1

    def test_create_fills_gaps(self):
        self.visual.references.create(reference='/b/', order=3)

        reference = self._add_reference(order=3)

        assert reference.order == 4

    def test_create_without_order_assigns_next(self):
        reference = self._add_reference()

        assert reference.order == 1

    def test_create_many_references_assigns_unique_orders(self):
        for index in range(5):
            reference = self._add_reference()

            assert reference.order == index + 1

        assert set(self.visual.references.values_list('order', flat=True)) == {0, 1, 2, 3, 4, 5}

    def test_update_keeps_explicit_order(self):
        first = self.visual.references.first()
        first.services.save_model_obj(reference='/a/', order=5)
        first.refresh_from_db()

        assert first.order == 5


class VisualConditionServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic, with_conditions=False)

        self.visual.conditions.create(state='green', order=0)

    def _add_condition(self, **kwargs) -> VisualCondition:
        condition = VisualCondition(visual=self.visual)
        condition.services.save_model_obj(state='red', **kwargs)
        condition.refresh_from_db()
        return condition

    def test_create_keeps_free_order(self):
        condition = self._add_condition(order=1)

        assert condition.order == 1

    def test_create_assigns_next_order_on_collision(self):
        condition = self._add_condition(order=0)

        assert condition.order == 1
