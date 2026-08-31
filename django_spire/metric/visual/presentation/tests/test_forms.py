from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.forms import SlideModelForm
from django_spire.metric.visual.presentation.tests.factories import (
    create_test_presentation,
    create_test_slide,
)


class SlideModelFormTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()
        self.slide = create_test_slide(self.presentation, order=0)

    def test_duplicate_order_is_invalid(self):
        form = SlideModelForm(
            data={'presentation': self.presentation.pk, 'name': 'dup', 'order': 0}
        )

        assert form.is_valid() is False
        assert 'order' in form.errors

    def test_unique_order_is_valid(self):
        form = SlideModelForm(
            data={'presentation': self.presentation.pk, 'name': 'next', 'order': 1}
        )

        assert form.is_valid() is True

    def test_same_order_on_own_row_is_valid(self):
        form = SlideModelForm(
            instance=self.slide,
            data={'presentation': self.presentation.pk, 'name': self.slide.name, 'order': 0},
        )

        assert form.is_valid() is True

    def test_duplicate_order_other_presentation_is_valid(self):
        other = create_test_presentation(name='other')

        form = SlideModelForm(
            data={'presentation': other.pk, 'name': 'dup', 'order': 0}
        )

        assert form.is_valid() is True
