from __future__ import annotations

import pytest
from django.db import IntegrityError

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.models import SlideSection
from django_spire.metric.visual.presentation.tests.factories import (
    create_test_presentation,
    create_test_section,
    create_test_slide,
)


class PresentationModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()

    def test_str(self):
        assert str(self.presentation) == self.presentation.name

    def test_set_deleted_deletes_slides(self):
        slide = create_test_slide(self.presentation)

        self.presentation.set_deleted()

        self.presentation.refresh_from_db()
        slide.refresh_from_db()

        assert self.presentation.is_deleted is True
        assert slide.is_deleted is True


class SlideModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()
        self.slide = create_test_slide(self.presentation)

    def test_str(self):
        assert str(self.slide) == self.slide.name

    def test_presentation_relation(self):
        assert self.slide.presentation == self.presentation

    def test_unique_order_per_presentation(self):
        with pytest.raises(IntegrityError):
            create_test_slide(self.presentation, order=self.slide.order)

    def test_set_deleted_deletes_sections(self):
        section = create_test_section(self.slide)

        self.slide.set_deleted()

        self.slide.refresh_from_db()
        section.refresh_from_db()

        assert self.slide.is_deleted is True
        assert section.is_deleted is True


class SlideSectionModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()
        self.slide = create_test_slide(self.presentation)
        self.section = create_test_section(self.slide, row=1, col=1)

    def test_str_with_visual(self):
        assert str(self.section) == f'{self.slide} - {self.section.visual}'

    def test_str_without_visual(self):
        section = create_test_section(self.slide, with_visual=False)

        assert str(section) == f'{self.slide} - Empty'

    def test_slide_relation(self):
        assert self.section.slide == self.slide

    def test_visual_nullable(self):
        section = create_test_section(self.slide, with_visual=False)

        assert section.visual is None
        assert section.visual_id is None

    def test_ordering(self):
        create_test_section(self.slide, row=2, col=3)
        create_test_section(self.slide, row=1, col=4)
        create_test_section(self.slide, row=1, col=2)

        sections = SlideSection.objects.for_slide(self.slide)

        # Includes the setUp section at (1, 1)
        assert [(s.row, s.col) for s in sections] == [(1, 1), (1, 2), (1, 4), (2, 3)]
