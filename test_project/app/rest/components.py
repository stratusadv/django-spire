from __future__ import annotations

from typing import TYPE_CHECKING

from django_glue import Glue

from django_spire.core.glue.components.scroll import QuerySetScrollComponent
from test_project.app.rest.models import Pirate
from test_project.app.rest.navigation import RestNavigation

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class PirateTableComponent(QuerySetScrollComponent):
    template = 'rest/component/pirate_table.html'
    item_template = 'rest/item/pirate_row.html'
    view_template = 'rest/page/pirate_table_page.html'

    search: str = Glue.attr('', editable=True)

    def __post_init__(self, request: HttpRequest) -> None:
        super().__post_init__(request)

        nav = RestNavigation()
        nav.page_title = 'Pirate Table'
        nav.breadcrumbs.add('Table')
        self.context_data.update(nav.as_context())

    def get_queryset(self) -> QuerySet[Pirate]:
        return Pirate.objects.active().search(self.search).order_by('last_name', 'first_name')
