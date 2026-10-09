from __future__ import annotations

import re

from typing import TYPE_CHECKING

from django_glue import Glue
from django_glue.exceptions import GlueRequestError, GlueRequestErrorCode

from django_spire.core.components import (
    BaseModelDeleteConfirmationComponent,
    ComponentDeleteOptions,
    ModelCrudScrollComponent,
    PageFormOptions,
    ScrollItemRenderMode,
)
from test_project.app.ordering.models import Duck

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class DuckDeleteConfirmationComponent(BaseModelDeleteConfirmationComponent):
    def perform_action(self) -> None:
        self.instance.ordering_services.processor.remove_from_objects(Duck.objects.active())
        self.instance.set_inactive()


class DuckListComponent(ModelCrudScrollComponent):
    template = 'ordering/component/duck_list.html'
    item_render_mode = ScrollItemRenderMode.SERVER
    item_template = 'ordering/item/duck_row.html'
    view_template = 'ordering/page/duck_list_component_page.html'

    item_delete_options = ComponentDeleteOptions(component=DuckDeleteConfirmationComponent)
    item_form_options = PageFormOptions('order:update', create_url_name='order:create')

    search: str = Glue.attr('', editable=True)

    def __post_init__(self, request: HttpRequest) -> None:
        super().__post_init__(request)

        self.access = Glue.Access.DELETE
        self.context_data.update({
            'page_title': 'Duck',
            'page_description': 'List Component',
            'breadcrumbs': [{'name': 'Ducks', 'href': None}],
        })

    def get_queryset(self) -> QuerySet[Duck]:
        return Duck.objects.active().filter(name__icontains=self.search).order_by('order')

    @Glue.attr(required_access=Glue.Access.CHANGE, skip_rerender=True)
    def duplicate(self, pk: int) -> None:
        duck = Duck.objects.active().get(pk=pk)
        duplicated, _created = Duck().services.save_model_obj(
            name=f'{duck.name} (Copy)',
            color=duck.color,
        )

        self.item_added(key=duplicated.pk)

    @Glue.attr(required_access=Glue.Access.CHANGE, skip_rerender=True)
    def paint(self, pk: int, color: str) -> None:
        if re.fullmatch(r'#[0-9a-fA-F]{6}', color) is None:
            raise GlueRequestError(
                code=GlueRequestErrorCode.INVALID_KWARGS,
                message='color must be a six-digit hex value.',
                details={'color': color},
            )

        Duck.objects.active().get(pk=pk).services.save_model_obj(color=color)
        self.item_changed(key=pk)
