from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Mapping

from django_glue import Glue


@dataclass(frozen=True)
class Tab:
    """
    Declares one tab inside a :class:`TabsComponent`.

    Provide exactly one target:
    - ``component``: a ``Glue.Component`` class or zero-argument factory callable
      (e.g. ``partial(EmployeeListComponent, is_active=True)``)
    - ``view_url``: a Django route URL loaded lazily via ``Glue.view(url)``
    - ``template``: a Django template rendered into the pane (with optional ``context``)
    - ``href``: a full-page link rendered as an ``<a>`` tag instead of swapping panes
    """

    id: str
    label: str
    component: Callable[[], Glue.Component] | None = None
    view_url: str | None = None
    template: str | None = None
    context: Mapping[str, Any] = field(default_factory=dict)
    href: str | None = None
    icon: str | None = None
    cache: bool | None = None
    view_method: Literal['GET', 'POST'] = 'GET'

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            message = 'Tab.id must be a non-empty string.'
            raise ValueError(message)

        if not isinstance(self.label, str) or not self.label.strip():
            message = 'Tab.label must be a non-empty string.'
            raise ValueError(message)

        targets = [
            name
            for name, value in (
                ('component', self.component),
                ('view_url', self.view_url),
                ('template', self.template),
                ('href', self.href),
            )
            if value is not None
        ]

        if len(targets) != 1:
            message = (
                f'Tab {self.id!r} must set exactly one of component, view_url, template, or href; '
                f'got {targets or "none"}.'
            )
            raise ValueError(message)

        if self.component is not None and not callable(self.component):
            message = f'Tab {self.id!r} component must be a Glue.Component class or factory callable.'
            raise TypeError(message)

        if self.view_method not in ('GET', 'POST'):
            message = f'Tab {self.id!r} view_method must be "GET" or "POST", not {self.view_method!r}.'
            raise ValueError(message)

    @property
    def kind(self) -> Literal['component', 'view', 'template', 'link']:
        if self.component is not None:
            return 'component'
        if self.view_url is not None:
            return 'view'
        if self.template is not None:
            return 'template'
        return 'link'

    @property
    def is_component(self) -> bool:
        return self.component is not None

    @property
    def is_view(self) -> bool:
        return self.view_url is not None

    @property
    def is_template(self) -> bool:
        return self.template is not None

    @property
    def is_link(self) -> bool:
        return self.href is not None

    def build_component(self) -> Glue.Component:
        if self.component is None:
            message = f'Tab {self.id!r} does not have a component.'
            raise ValueError(message)

        instance = self.component()

        if not isinstance(instance, Glue.Component):
            message = (
                f'Tab {self.id!r} component factory must return a Glue.Component instance, '
                f'got {type(instance).__name__}.'
            )
            raise TypeError(message)

        return instance
