from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.core.components import QuerySetScrollComponent
from test_project.app.history.models import HistoryExample

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class HistoryListComponent(QuerySetScrollComponent):
    template = 'history/component/history_list.html'
    view_template = 'history/page/history_list_component_page.html'
    fields = ('name', 'description')

    def __post_init__(self, request: HttpRequest) -> None:
        super().__post_init__(request)

        self.context_data.update({
            'page_title': 'History Example',
            'page_description': 'List Component',
            'breadcrumbs': [{'name': 'History Examples', 'href': None}],
        })

    def get_queryset(self) -> QuerySet[HistoryExample]:
        return HistoryExample.objects.active().order_by('name')
