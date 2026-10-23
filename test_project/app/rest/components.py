from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django_glue import Glue

from django_spire.contrib.rest.connector.exceptions import RestConnectorError
from django_spire.core.components import (
    BaseScrollComponent,
    QuerySetScrollComponent,
    ScrollItemRenderMode,
)
from test_project.app.rest.models import Pirate
from test_project.app.rest.navigation import RestNavigation
from test_project.app.rest.rest import PirateRestSchema

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class PirateApiListComponent(BaseScrollComponent):
    item_render_mode = ScrollItemRenderMode.SERVER
    item_template = 'rest/item/pirate_api_row.html'
    view_template = 'django_spire/component/page/full_page.html'

    def __post_init__(self, request: HttpRequest) -> None:
        super().__post_init__(request)

        nav = RestNavigation()
        nav.page_title = 'Pirate API List'
        nav.breadcrumbs.add('API List')
        self.context_data.update(nav.as_context())

    def get_items(self, offset: int, limit: int) -> list[PirateRestSchema]:
        return list(PirateRestSchema.objects.with_request_params(skip=offset, limit=limit))

    def get_item(self, key: Any) -> PirateRestSchema | None:
        try:
            return PirateRestSchema.objects.get(id=key)
        except (LookupError, RestConnectorError):
            return None

    def get_item_key(self, item: PirateRestSchema) -> int:
        return item.id


class PirateTableComponent(QuerySetScrollComponent):
    template = 'rest/component/pirate_table.html'
    item_render_mode = ScrollItemRenderMode.SERVER
    item_template = 'rest/item/pirate_row.html'
    view_template = 'django_spire/component/page/full_page.html'

    search: str = Glue.attr('', editable=True)

    def __post_init__(self, request: HttpRequest) -> None:
        super().__post_init__(request)

        nav = RestNavigation()
        nav.page_title = 'Pirate Table'
        nav.breadcrumbs.add('Table')
        self.context_data.update(nav.as_context())

    def get_queryset(self) -> QuerySet[Pirate]:
        return Pirate.objects.active().search(self.search).order_by('last_name', 'first_name')
