from __future__ import annotations

import json

from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, ClassVar, TYPE_CHECKING

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe
from django_glue import Glue
from django_glue.exceptions import GlueAuthorizationError
from django_glue.glue import address
from django_glue.glue.context import GlueContextManager
from django_glue.response import GlueResponse, GlueTemplateResponse

from django_spire.core.components.tab.options import Tab

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.http import HttpRequest


class TabsComponent(Glue.Component, ABC):
    """
    A tabbed container whose panes are loaded lazily and may host Glue
    components, Django fragment views (via ``Glue.view``), plain templates, or
    full-page links.

    Subclasses implement ``get_tabs()`` returning a sequence of :class:`Tab`
    items (aliased as ``self.Tab``). Only the initially active tab is rendered
    on first paint; other tabs stay empty until selected.

    - ``url_param``: query parameter synced with ``history.replaceState`` and
      read from ``request.GET`` on first render (default ``'tab'``; set to
      ``None`` to disable).
    - ``cache_tabs``: whether visited panes stay mounted across switches
      (default ``True``; overridable per tab via ``Tab(..., cache=False)``).
    - ``tab_invalidated``: Glue event wired to ``invalidateTab(tab_id)`` so
      listeners can mark a cached tab stale or force-refresh the active tab.
    """

    Tab = Tab

    template = 'django_spire/component/tab/tabs.html'
    view_template = 'django_spire/component/page/full_page.html'

    url_param: ClassVar[str | None] = 'tab'
    default_tab: ClassVar[str | None] = None
    cache_tabs: ClassVar[bool] = True

    active_tab: str | None = Glue.ComponentParameter(None)

    tab_invalidated = Glue.event()

    def __post_init__(self, request: HttpRequest) -> None:
        super().__post_init__(request)

        valid_pane_ids = [tab.id for tab in self.tabs if not tab.is_link]

        if not valid_pane_ids:
            self.active_tab = None
            return

        if self.active_tab not in valid_pane_ids:
            requested = request.GET.get(self.url_param) if self.url_param else None

            if requested in valid_pane_ids:
                self.active_tab = requested
            elif self.default_tab in valid_pane_ids:
                self.active_tab = self.default_tab
            else:
                self.active_tab = valid_pane_ids[0]

    @abstractmethod
    def get_tabs(self) -> Sequence[Tab]:
        """Return the ordered :class:`Tab` definitions to display."""

    @cached_property
    def tabs(self) -> tuple[Tab, ...]:
        resolved = tuple(self.get_tabs())
        seen_ids: set[str] = set()

        for tab in resolved:
            if not isinstance(tab, Tab):
                message = f'{type(self).__name__}.get_tabs() must return Tab instances, got {type(tab).__name__}.'
                raise ImproperlyConfigured(message)

            if tab.id in seen_ids:
                message = f'{type(self).__name__}.get_tabs() contains duplicate tab id {tab.id!r}.'
                raise ImproperlyConfigured(message)

            seen_ids.add(tab.id)

        return resolved

    def get_tab(self, tab_id: str | None) -> Tab | None:
        if tab_id is None:
            return None

        for tab in self.tabs:
            if tab.id == tab_id:
                return tab

        return None

    @property
    def active_tab_obj(self) -> Tab | None:
        return self.get_tab(self.active_tab)

    def should_cache_tab(self, tab: Tab) -> bool:
        return self.cache_tabs if tab.cache is None else tab.cache

    @cached_property
    def active_tab_html(self) -> SafeString:
        tab = self.active_tab_obj

        if tab is None or tab.is_link or tab.is_view or self.request is None:
            return mark_safe('')

        if tab.is_component:
            try:
                html = self._render_component_tab(self.request, tab).html or ''
                return mark_safe(html)  # noqa: S308
            except GlueAuthorizationError:
                return mark_safe('')

        return self._render_template_tab(self.request, tab)

    @property
    def tabs_config_json(self) -> str:
        active = self.active_tab_obj
        initial_loaded = (
            [active.id]
            if active is not None and (active.is_component or active.is_template)
            else []
        )

        config: dict[str, Any] = {
            'activeTab': self.active_tab,
            'initialLoaded': initial_loaded,
            'tabs': {
                tab.id: {
                    'cache': self.should_cache_tab(tab),
                    'kind': tab.kind,
                    'viewMethod': tab.view_method,
                    'viewUrl': tab.view_url,
                }
                for tab in self.tabs
            },
            'urlParam': self.url_param,
        }

        return json.dumps(config)

    def _render_component_tab(self, request: HttpRequest, tab: Tab) -> GlueResponse:
        child = tab.build_component()
        child._address = address.item(self.address, f'tab:{tab.id}')
        child._ancestors = self.lineage
        GlueContextManager(request).add_glue(child)
        return child.render()

    def _render_template_tab(self, request: HttpRequest, tab: Tab) -> SafeString:
        if tab.template is None:
            return mark_safe('')

        return render_to_string(
            tab.template,
            {**tab.context, 'component': self, 'tab': tab},
            request=request,
        )

    @Glue.attr(required_access=Glue.Access.VIEW, skip_rerender=True)
    def load_tab(self, request: HttpRequest, tab_id: str) -> GlueResponse:
        tab = self.get_tab(tab_id)

        if tab is None or tab.is_link or tab.is_view:
            message = f'{type(self).__name__} has no loadable tab {tab_id!r}.'
            raise PermissionDenied(message)

        if tab.is_component:
            try:
                return self._render_component_tab(request, tab)
            except GlueAuthorizationError as error:
                raise PermissionDenied from error

        return GlueTemplateResponse(
            request,
            tab.template,
            {**tab.context, 'component': self, 'tab': tab},
        )
