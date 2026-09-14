from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.signage import forms


class SignageModelFormTestCase(BaseTestCase):
    data = {
        'name': 'test signage',
        'title': '',
        'description': 'signage description',
        'slide_display_seconds': 0,
    }

    def test_slide_display_seconds_coerces_zero_to_one(self) -> None:
        form = forms.SignageModelForm(data={**self.data, 'slide_display_seconds': 0})

        assert form.is_valid()
        assert form.cleaned_data['slide_display_seconds'] == 1

    def test_slide_display_seconds_below_one_coerces_to_one(self) -> None:
        form = forms.SignageModelForm(data={**self.data, 'slide_display_seconds': 1})

        assert form.is_valid()
        assert form.cleaned_data['slide_display_seconds'] == 1

    def test_slide_display_seconds_above_one_is_preserved(self) -> None:
        form = forms.SignageModelForm(data={**self.data, 'slide_display_seconds': 45})

        assert form.is_valid()
        assert form.cleaned_data['slide_display_seconds'] == 45
