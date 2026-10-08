from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.models import Slide
from django_spire.metric.visual.presentation.tests.factories import (
    create_test_presentation,
    create_test_slide,
)


class SlideServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()
        create_test_slide(self.presentation, order=0)

    def _add_slide(self, **kwargs) -> Slide:
        slide = Slide(presentation=self.presentation)
        slide.services.save_model_obj(name='new_slide', **kwargs)
        slide.refresh_from_db()
        return slide

    def test_create_keeps_free_order(self):
        slide = self._add_slide(order=1)

        assert slide.order == 1

    def test_create_assigns_next_order_on_collision(self):
        slide = self._add_slide(order=0)

        assert slide.order == 1

    def test_create_without_order_assigns_next(self):
        slide = self._add_slide()

        assert slide.order == 1

    def test_create_many_slides_assigns_unique_orders(self):
        for index in range(5):
            slide = self._add_slide(order=0)

            assert slide.order == index + 1

        orders = set(self.presentation.slides.values_list('order', flat=True))
        assert orders == {0, 1, 2, 3, 4, 5}

    def test_next_order_is_zero_without_slides(self):
        presentation = create_test_presentation()

        assert Slide.services.next_order(presentation.slides) == 0

    def test_next_order_appends_after_max_order(self):
        create_test_slide(self.presentation, order=5)

        assert Slide.services.next_order(self.presentation.slides) == 6

    def test_next_order_ignores_gaps_below_max(self):
        create_test_slide(self.presentation, order=2)

        assert Slide.services.next_order(self.presentation.slides) == 3
