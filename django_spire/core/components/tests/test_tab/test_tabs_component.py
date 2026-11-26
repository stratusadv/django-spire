from __future__ import annotations

from functools import partial
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase
from django_glue import Glue
from django_glue.resolver.attribute_call.context import AttributeCallRequestContext

from django_spire.core.components import Tab, TabsComponent


class _SampleChildComponent(Glue.Component):
    template = 'django_spire/item/no_data_item.html'

    label: str = Glue.ComponentParameter('default')


class TabOptionsTestCase(SimpleTestCase):
    def test_validates_target_exclusivity_and_arguments(self) -> None:
        with pytest.raises(ValueError, match=r'Tab\.id'):
            Tab('', 'Empty', href='/x/')

        with pytest.raises(ValueError, match=r'Tab\.label'):
            Tab('a', '', href='/x/')

        with pytest.raises(ValueError, match='exactly one'):
            Tab('a', 'No Target')

        with pytest.raises(ValueError, match='exactly one'):
            Tab('a', 'Two Targets', href='/x/', view_url='/y/')

        with pytest.raises(TypeError, match='callable'):
            Tab('a', 'Bad Component', component='not-callable')  # type: ignore[arg-type]

        with pytest.raises(ValueError, match='view_method'):
            Tab('a', 'Bad Method', view_url='/x/', view_method='DELETE')  # type: ignore[arg-type]

    def test_build_component_validates_return_type(self) -> None:
        good_tab = Tab('ok', 'OK', component=partial(_SampleChildComponent, label='hi'))
        built = good_tab.build_component()

        assert isinstance(built, _SampleChildComponent)
        assert built.label == 'hi'

        bad_tab = Tab('bad', 'Bad', component=lambda: 'not-a-component')  # type: ignore[arg-type,return-value]
        with pytest.raises(TypeError, match=r'Glue\.Component'):
            bad_tab.build_component()


class TabsComponentTestCase(SimpleTestCase):
    def _request(self, path: str = '/') -> object:
        request = RequestFactory().get(path)
        request.user = SimpleNamespace(is_authenticated=True, is_superuser=True)
        request.session = SimpleNamespace(session_key='tabs-test-session')
        return request

    def test_resolves_active_tab_from_url_param_default_or_first_pane(self) -> None:
        class DemoTabsComponent(TabsComponent):
            default_tab = 'second'

            def get_tabs(self) -> list[Tab]:
                return [
                    self.Tab('ext', 'External', href='/external/'),
                    self.Tab('first', 'First', component=partial(_SampleChildComponent, label='one')),
                    self.Tab('second', 'Second', component=partial(_SampleChildComponent, label='two')),
                ]

        default_comp = DemoTabsComponent()
        default_comp.introduce(self._request('/'))
        assert default_comp.active_tab == 'second'

        url_comp = DemoTabsComponent()
        url_comp.introduce(self._request('/?tab=first'))
        assert url_comp.active_tab == 'first'

        invalid_url_comp = DemoTabsComponent()
        invalid_url_comp.introduce(self._request('/?tab=ext'))
        assert invalid_url_comp.active_tab == 'second'

    def test_renders_only_active_tab_lazily_on_first_paint(self) -> None:
        first_factory = MagicMock(side_effect=lambda: _SampleChildComponent(label='one'))
        second_factory = MagicMock(side_effect=lambda: _SampleChildComponent(label='two'))

        class LazyTabsComponent(TabsComponent):
            def get_tabs(self) -> list[Tab]:
                return [
                    self.Tab('first', 'First', component=first_factory),
                    self.Tab('second', 'Second', component=second_factory, cache=False),
                    self.Tab('view', 'View Tab', view_url='/fragment/', view_method='POST'),
                    self.Tab('link', 'External', href='/go/'),
                ]

        request = self._request('/')
        component = LazyTabsComponent()
        component.introduce(request)
        html = component.render().html

        assert first_factory.call_count == 1
        assert second_factory.call_count == 0
        assert 'data-tab-pane="first"' in html
        assert 'data-tab-pane="second"' in html
        assert 'href="/go/"' in html
        assert component.should_cache_tab(component.get_tab('first')) is True
        assert component.should_cache_tab(component.get_tab('second')) is False

    def test_load_tab_returns_component_or_template_and_refuses_others(self) -> None:
        class MixedTabsComponent(TabsComponent):
            def get_tabs(self) -> list[Tab]:
                return [
                    self.Tab('comp', 'Component', component=partial(_SampleChildComponent, label='loaded')),
                    self.Tab('tpl', 'Template', template='django_spire/item/no_data_item.html'),
                    self.Tab('view', 'View', view_url='/fragment/'),
                    self.Tab('link', 'Link', href='/other/'),
                ]

        request = self._request('/')
        component = MixedTabsComponent()
        component.introduce(request)

        comp_response = component.load_tab(request, tab_id='comp')
        assert comp_response.html is not None
        assert 'data-glue-address' in comp_response.html
        assert 'data-glue-objects' in comp_response.html

        tpl_response = component.load_tab(request, tab_id='tpl')
        assert tpl_response.html is not None
        assert 'No data to display' in tpl_response.html

        for disallowed in ('view', 'link', 'missing'):
            with pytest.raises(PermissionDenied):
                component.load_tab(request, tab_id=disallowed)

    def test_load_tab_wire_call_returns_child_html_without_rerendering_tabs(self) -> None:
        class WireTabsComponent(TabsComponent):
            def get_tabs(self) -> list[Tab]:
                return [
                    self.Tab('first', 'First', component=partial(_SampleChildComponent, label='one')),
                    self.Tab('second', 'Second', component=partial(_SampleChildComponent, label='two')),
                ]

        request = self._request('/')
        component = WireTabsComponent()
        component.introduce(request)

        post_request = RequestFactory().post('/__dg__/callable_attribute/')
        post_request.user = request.user
        post_request.session = request.session

        context = AttributeCallRequestContext(
            request=post_request,
            target_glue_policy=component.policy,
            target_attribute_name='load_tab',
            target_attribute_call_kwargs={'tab_id': 'second'},
        )
        rebuilt = WireTabsComponent.from_attribute_call_resolver_context(context)
        entry, introduced = rebuilt.process_attribute_call(context)

        assert entry['address'] == component.address
        assert 'data-glue-address' in entry['html']
        assert f'{component.address}[tab:second]' in entry['html']
        assert any(obj['address'] == f'{component.address}[tab:second]' for obj in introduced)

    def test_rejects_duplicate_tab_ids(self) -> None:
        class DuplicateTabsComponent(TabsComponent):
            def get_tabs(self) -> list[Tab]:
                return [
                    self.Tab('dup', 'One', href='/1/'),
                    self.Tab('dup', 'Two', href='/2/'),
                ]

        with pytest.raises(ImproperlyConfigured, match='duplicate tab id'):
            _ = DuplicateTabsComponent().tabs

    def test_static_tab_templates_render_tab_id_and_url_param(self) -> None:
        tab_html = render_to_string(
            'django_spire/tab/tab.html',
            {'tab_id': 'inactive', 'tab_name': 'Inactive'},
        )
        assert 'data-tab-id="inactive"' in tab_html

        section_html = Template(
            "{% extends 'django_spire/tab/section.html' %}"
            '{% block tab_url_param %}status{% endblock %}'
        ).render(Context({}))
        assert "spireTabs({urlParam: 'status'})" in section_html
