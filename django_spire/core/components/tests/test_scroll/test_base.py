from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.test import RequestFactory
from django_glue import Glue
from django_glue.exceptions import GlueRequestError

from django_spire.core.components.scroll import BaseScrollComponent, ScrollItemRenderMode
from django_spire.core.tests.test_cases import BaseTestCase

if TYPE_CHECKING:
    from django.http import HttpRequest


class NumberScrollComponent(BaseScrollComponent):
    template = 'comment/component/comment_list.html'
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


class RenderedNumberScrollComponent(NumberScrollComponent):
    template = 'django_spire/component/scroll/base.html'
    item_render_mode = ScrollItemRenderMode.SERVER
    item_template = 'comment/item/scroll_item.html'


class ClientItemTemplateScrollComponent(NumberScrollComponent):
    template = 'django_spire/component/scroll/base.html'
    item_template = 'comment/item/comment_row.html'


class UnextendedTemplateScrollComponent(NumberScrollComponent):
    template = 'comment/item/comment_row.html'


class UnextendedItemTemplateScrollComponent(NumberScrollComponent):
    template = 'django_spire/component/scroll/base.html'
    item_render_mode = ScrollItemRenderMode.SERVER
    item_template = 'comment/item/comment_row.html'


class ServerItemTemplateOnClientScrollComponent(NumberScrollComponent):
    template = 'django_spire/component/scroll/base.html'
    item_template = 'comment/item/scroll_item.html'


class TemplatelessServerScrollComponent(NumberScrollComponent):
    template = 'django_spire/component/scroll/base.html'
    item_render_mode = ScrollItemRenderMode.SERVER


class StringRenderModeScrollComponent(NumberScrollComponent):
    template = 'django_spire/component/scroll/base.html'
    item_render_mode = 'server'


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

    def test_first_batch_data_carries_the_first_batch_only_in_data_mode(self) -> None:
        data_component = self._introduce(NumberScrollComponent(count=4))
        rendered_component = self._introduce(RenderedNumberScrollComponent(count=4))

        assert data_component.first_batch_data == {
            'items': [
                {'pk': 0, 'name': 'Item 0'},
                {'pk': 1, 'name': 'Item 1'},
                {'pk': 2, 'name': 'Item 2'},
            ],
            'keys': [0, 1, 2],
            'has_more': True,
        }
        assert rendered_component.first_batch_data is None

    def test_load_items_returns_the_batch_at_an_offset(self) -> None:
        component = self._introduce(NumberScrollComponent(count=7))
        expected_by_offset = {
            3: ([3, 4, 5], True),
            6: ([6], False),
            7: ([], False),
            100: ([], False),
        }

        for offset, (keys, has_more) in expected_by_offset.items():
            batch = component.load_items(component.request, offset)

            assert batch['keys'] == keys
            assert [item['pk'] for item in batch['items']] == keys
            assert batch['has_more'] is has_more

    def test_load_items_rejects_a_negative_offset(self) -> None:
        component = self._introduce(NumberScrollComponent(count=7))

        with pytest.raises(GlueRequestError):
            component.load_items(component.request, -1)

        assert component.load_items(component.request, 0)['keys'] == [0, 1, 2]

    def test_load_item_returns_one_item_or_nothing(self) -> None:
        component = self._introduce(NumberScrollComponent(count=4))

        assert component.load_item(component.request, 2) == {
            'item': {'pk': 2, 'name': 'Item 2'},
            'key': 2,
        }
        assert component.load_item(component.request, 4) is None

    def test_load_items_renders_each_item_and_marks_whether_more_remain(self) -> None:
        component = self._introduce(RenderedNumberScrollComponent(count=4))

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
        component = self._introduce(RenderedNumberScrollComponent(count=4))

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

    def test_a_server_row_template_on_a_client_rendered_list_is_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='item_template'):
            self._introduce(ServerItemTemplateOnClientScrollComponent())

    def test_rendering_on_the_server_needs_an_item_template(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='needs an item_template'):
            self._introduce(TemplatelessServerScrollComponent())

    def test_a_render_mode_that_is_not_the_enum_is_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='ScrollItemRenderMode'):
            self._introduce(StringRenderModeScrollComponent())

    def test_a_client_rendered_list_draws_its_item_template_in_the_item_block(self) -> None:
        component = self._introduce(ClientItemTemplateScrollComponent(count=2))

        html = render_to_string(component.template, {'component': component})

        assert component.renders_items_on_server is False
        assert component.first_batch_data['keys'] == [0, 1]
        assert 'x-text="item.name"' in html
        assert 'rendersRows: false' in html

    def test_valid_templates_are_accepted_and_recorded(self) -> None:
        self._introduce(NumberScrollComponent())
        self._introduce(RenderedNumberScrollComponent())
        self._introduce(ClientItemTemplateScrollComponent())

        assert NumberScrollComponent in BaseScrollComponent._validated_classes
        assert RenderedNumberScrollComponent in BaseScrollComponent._validated_classes
        assert ClientItemTemplateScrollComponent in BaseScrollComponent._validated_classes

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
