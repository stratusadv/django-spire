from __future__ import annotations

import pytest
from django.test import TestCase, override_settings

from django_spire.core.search.registry import get_search_class, get_search_registry


@override_settings(DJANGO_SPIRE_SEARCH_REGISTRY={'TASK': 'test_project.app.task.search.TaskSearch'})
class TestSearchRegistry(TestCase):
    def test_get_search_class(self) -> None:
        search_class = get_search_class('TASK')

        assert search_class is not None
        assert search_class.search_key == 'TASK'

    def test_get_search_class_missing_key_returns_none(self) -> None:
        assert get_search_class('NO_SUCH_KEY') is None

    def test_get_search_registry(self) -> None:
        registry = get_search_registry()

        assert 'TASK' in registry
        assert registry['TASK'].search_key == 'TASK'

    @override_settings(DJANGO_SPIRE_SEARCH_REGISTRY={'TASK': 'django_spire.constants.__VERSION__'})
    def test_non_base_search_subclass_raises(self) -> None:
        with pytest.raises(TypeError):
            get_search_registry()

    @override_settings(
        DJANGO_SPIRE_SEARCH_REGISTRY={'OTHER': 'test_project.app.task.search.TaskSearch'}
    )
    def test_search_key_does_not_need_to_match(self) -> None:
        registry = get_search_registry()

        assert 'OTHER' in registry
        assert registry['OTHER'].search_key == 'TASK'


@override_settings(DJANGO_SPIRE_SEARCH_REGISTRY={})
class TestEmptySearchRegistry(TestCase):
    def test_empty_registry(self) -> None:
        assert get_search_registry() == {}
