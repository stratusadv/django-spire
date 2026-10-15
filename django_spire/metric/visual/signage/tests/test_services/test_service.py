from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.tests.factories import create_test_presentation
from django_spire.metric.visual.signage.models import SignagePresentation
from django_spire.metric.visual.signage.tests.factories import create_test_link, create_test_signage


class SignagePresentationServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.signage = create_test_signage()
        create_test_link(self.signage, order=0)

    def _add_link(self, **kwargs) -> SignagePresentation:
        presentation = create_test_presentation()
        link = SignagePresentation(signage=self.signage)
        link.services.save_model_obj(presentation=presentation, **kwargs)
        link.refresh_from_db()
        return link

    def test_create_keeps_free_order(self):
        link = self._add_link(order=1)

        assert link.order == 1

    def test_create_assigns_next_order_on_collision(self):
        link = self._add_link(order=0)

        assert link.order == 1

    def test_create_without_order_assigns_next(self):
        link = self._add_link()

        assert link.order == 1

    def test_create_many_links_assigns_unique_orders(self):
        for index in range(5):
            link = self._add_link(order=0)

            assert link.order == index + 1

        orders = set(self.signage.signage_presentations.values_list('order', flat=True))
        assert orders == {0, 1, 2, 3, 4, 5}

    def test_next_order_is_zero_without_links(self):
        signage = create_test_signage()

        assert SignagePresentation.services.next_order(signage.signage_presentations) == 0

    def test_next_order_appends_after_max_order(self):
        create_test_link(self.signage, order=5)

        assert SignagePresentation.services.next_order(self.signage.signage_presentations) == 6

    def test_next_order_ignores_gaps_below_max(self):
        create_test_link(self.signage, order=2)

        assert SignagePresentation.services.next_order(self.signage.signage_presentations) == 3
