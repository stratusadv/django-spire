from __future__ import annotations

import re

from typing import TYPE_CHECKING, Any

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.test import RequestFactory
from django_glue import Glue
from django_glue.exceptions import GlueRequestError

from django_spire.core.components.scroll import BaseScrollComponent
from django_spire.core.tests.test_cases import BaseTestCase

if TYPE_CHECKING:
    from django.http import HttpRequest


class NumberScrollComponent(BaseScrollComponent):
    template = 'django_spire/component/scroll/scroll.html'
    item_template = 'comment/item/scroll_item.html'
    batch_size = 3

    count: int = Glue.ComponentParameter(0)

    def get_items(self, offset: int, limit: int) -> list[dict[str, Any]]:
        numbers = range(self.count)[offset:offset + limit]

        return [{'pk': number, 'name': f'Item {number}'} for number in numbers]

    def get_item(self, key: Any) -> dict[str, Any] | None:
        if int(key) not in range(self.count):
            return None

        return {'pk': int(key), 'name': f'Item {key}'}

    def get_item_key(self, item: dict[str, Any]) -> int:
        return item['pk']


class UnextendedTemplateScrollComponent(NumberScrollComponent):
    template = 'comment/item/item.html'


class UnextendedItemTemplateScrollComponent(NumberScrollComponent):
    item_template = 'task/item/task_row.html'


class TemplatelessScrollComponent(NumberScrollComponent):
    item_template = None


class SkippedSuperScrollComponent(NumberScrollComponent):
    def __post_init__(self, request: HttpRequest) -> None:
        self.count = 5


class CallingSuperScrollComponent(NumberScrollComponent):
    def __post_init__(self, request: HttpRequest) -> None:
        super().__post_init__(request)
        self.count = 5


class BaseScrollComponentTestCase(BaseTestCase):
    def _introduce(self, component: BaseScrollComponent) -> BaseScrollComponent:
        request = RequestFactory().get('/')
        request.user = self.super_user
        request.session = self.client.session

        return Glue.object(request, component)

    def test_first_batch_on_each_side_of_the_batch_size(self) -> None:
        expected_by_count = {
            0: ([], False),
            2: ([0, 1], False),
            3: ([0, 1, 2], False),
            4: ([0, 1, 2], True),
        }

        for count, (keys, has_more) in expected_by_count.items():
            batch = self._introduce(NumberScrollComponent(count=count)).first_batch

            assert batch.keys == keys
            assert [item['pk'] for item in batch.items] == keys
            assert batch.has_more is has_more

    def test_load_items_renders_the_batch_at_an_offset(self) -> None:
        component = self._introduce(NumberScrollComponent(count=7))
        expected_by_offset = {
            3: (['3', '4', '5'], 'true'),
            6: (['6'], 'false'),
            7: ([], 'false'),
            100: ([], 'false'),
        }

        for offset, (keys, has_more) in expected_by_offset.items():
            html = component.load_items(component.request, offset).html

            assert re.findall(r'data-scroll-key="(\d+)"', html) == keys
            assert f'data-scroll-has-more="{has_more}"' in html

    def test_load_items_rejects_a_negative_offset(self) -> None:
        component = self._introduce(NumberScrollComponent(count=7))

        with pytest.raises(GlueRequestError):
            component.load_items(component.request, -1)

        assert 'data-scroll-key="0"' in component.load_items(component.request, 0).html

    def test_load_items_renders_each_item_and_marks_whether_more_remain(self) -> None:
        component = self._introduce(NumberScrollComponent(count=4))

        first_html = component.load_items(component.request, 0).html
        last_html = component.load_items(component.request, 3).html

        assert [f'data-scroll-key="{key}"' in first_html for key in range(4)] == [
            True,
            True,
            True,
            False,
        ]
        assert 'Item 2' in first_html
        assert 'data-scroll-has-more="true"' in first_html

        assert last_html.count('data-scroll-key=') == 1
        assert 'data-scroll-key="3"' in last_html
        assert 'data-scroll-has-more="false"' in last_html

    def test_load_item_renders_one_row_without_a_batch_end(self) -> None:
        component = self._introduce(NumberScrollComponent(count=4))

        html = component.load_item(component.request, 2).html

        assert html.count('data-scroll-key=') == 1
        assert 'data-scroll-key="2"' in html
        assert 'Item 2' in html
        assert 'data-scroll-batch-end' not in html
        assert component.load_item(component.request, 4) is None

    def test_a_template_that_does_not_extend_the_scroll_template_is_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='template'):
            self._introduce(UnextendedTemplateScrollComponent())

        assert UnextendedTemplateScrollComponent not in BaseScrollComponent._validated_classes

    def test_an_item_template_that_does_not_extend_a_row_template_is_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='item_template'):
            self._introduce(UnextendedItemTemplateScrollComponent())

        assert UnextendedItemTemplateScrollComponent not in BaseScrollComponent._validated_classes

    def test_a_list_needs_an_item_template(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='needs an item_template'):
            self._introduce(TemplatelessScrollComponent())

    def test_a_list_renders_its_first_batch_with_the_page(self) -> None:
        component = self._introduce(NumberScrollComponent(count=2))

        html = render_to_string(component.template, {'component': component})

        assert 'data-scroll-key="1"' in html
        assert 'Item 1' in html
        assert 'rendersRows: true' in html

    def test_valid_templates_are_accepted_and_recorded(self) -> None:
        self._introduce(NumberScrollComponent())

        assert NumberScrollComponent in BaseScrollComponent._validated_classes

    def test_post_init_that_skips_super_is_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match=r'super\(\)\.__post_init__'):
            self._introduce(SkippedSuperScrollComponent())

    def test_post_init_that_calls_super_is_accepted(self) -> None:
        component = self._introduce(CallingSuperScrollComponent())

        assert component.first_batch.keys == [0, 1, 2]
        assert component.first_batch.has_more is True

    def test_the_base_cannot_be_used_without_its_item_methods(self) -> None:
        with pytest.raises(TypeError):
            BaseScrollComponent()
