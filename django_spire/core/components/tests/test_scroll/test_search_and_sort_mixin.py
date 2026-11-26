from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.test import SimpleTestCase
from django_glue import Glue

from django_spire.core.components import SearchAndSortMixin


class _SampleSortChoices(models.TextChoices):
    NAME = 'name', 'Name'
    CREATED = '-created_datetime', 'Newest'


class _BaseDummyComponent(Glue.Component):
    template = 'django_spire/component/scroll/scroll.html'


class SearchAndSortMixinTestCase(SimpleTestCase):
    def test_infers_sort_choices_from_default_sort(self) -> None:
        class InferredListComponent(SearchAndSortMixin, _BaseDummyComponent):
            default_sort = _SampleSortChoices.CREATED

        component = InferredListComponent()

        assert InferredListComponent.sort_choices is _SampleSortChoices
        assert component.search == ''
        assert component.sort is _SampleSortChoices.CREATED

        component.sort = 'name'
        assert component.sort is _SampleSortChoices.NAME

    def test_defaults_sort_to_first_choice_when_only_sort_choices_set(self) -> None:
        class ChoicesOnlyListComponent(SearchAndSortMixin, _BaseDummyComponent):
            sort_choices = _SampleSortChoices

        component = ChoicesOnlyListComponent()

        assert component.sort is _SampleSortChoices.NAME

    def test_search_only_when_neither_sort_option_is_set(self) -> None:
        class SearchOnlyListComponent(SearchAndSortMixin, _BaseDummyComponent):
            pass

        component = SearchOnlyListComponent()

        assert component.search == ''
        assert not hasattr(component, 'sort')

    def test_refuses_raw_string_default_sort_without_sort_choices(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='default_sort must be a Django Choices member'):
            class BadDefaultSortComponent(SearchAndSortMixin, _BaseDummyComponent):
                default_sort = 'name'

    def test_refuses_non_choices_sort_choices(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='sort_choices must be a Django Choices subclass'):
            class BadSortChoicesComponent(SearchAndSortMixin, _BaseDummyComponent):
                sort_choices = [('name', 'Name')]  # type: ignore[assignment]
