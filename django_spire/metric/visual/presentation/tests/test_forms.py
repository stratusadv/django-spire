from __future__ import annotations

from django import forms

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.forms import SlideModelForm, SlideSectionModelForm
from django_spire.metric.visual.presentation.tests.factories import (
    create_test_presentation,
    create_test_section,
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

        form = SlideModelForm(data={'presentation': other.pk, 'name': 'dup', 'order': 0})

        assert form.is_valid() is True


class SlideSectionModelFormTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()
        self.slide = create_test_slide(self.presentation, order=0)
        self.section = create_test_section(self.slide, row=1, col=1)

    def _section_data(self, **overrides) -> dict:
        data = {'slide': self.slide.pk, 'visual': '', 'row': '2', 'col': '2'}
        data.update(overrides)
        return data

    def test_row_and_col_are_dropdowns_limited_to_three(self):
        form = SlideSectionModelForm()

        for name in ('row', 'col'):
            field = form.fields[name]
            assert isinstance(field.widget, forms.Select)
            assert [str(value) for value, _ in field.choices] == ['0', '1', '2']

    def test_occupied_cell_is_invalid(self):
        form = SlideSectionModelForm(data=self._section_data(row='1', col='1'))

        assert form.is_valid() is False
        assert 'col' in form.errors

    def test_free_cell_is_valid(self):
        form = SlideSectionModelForm(data=self._section_data(row='2', col='2'))

        assert form.is_valid() is True

    def test_editing_same_cell_is_valid(self):
        form = SlideSectionModelForm(
            instance=self.section, data=self._section_data(row='1', col='1')
        )

        assert form.is_valid() is True

    def test_rows_and_cols_beyond_grid_still_selectable(self):
        section = create_test_section(self.slide, row=5, col=4)

        form = SlideSectionModelForm(instance=section)

        assert ('5', 'Row 6') in form.fields['row'].choices
        assert ('4', 'Column 5') in form.fields['col'].choices
