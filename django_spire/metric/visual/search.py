from __future__ import annotations

from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse

from django_spire.core.search import Search

from django_spire.metric.visual import models


class VisualSearch(Search):
    model_class = models.Visual
    searchable_fields = ['name', 'description', 'statistic__name', 'statistic__group__name']
    name = 'Visuals'
    icon = 'bi-clipboard-data'
    permission_required = 'django_spire_metric_visual.view_visual'

    searchable_commands = [
        Search.Command(
            name='New Visual',
            icon='bi-plus-lg',
            url=reverse('django_spire:metric:visual:form:create'),
            action=Search.Command.Action.OPEN_URL_CURRENT_TAB,
            description='Create a new visual',
            permission_required='django_spire_metric_visual.add_visual',
        )
    ]

    def base_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model_class.objects.with_statistic().not_deleted()

    def generate_list_url(self) -> str:
        return reverse('django_spire:metric:visual:page:list')

    def generate_detail_url(self, obj: models.Visual) -> str:
        return reverse('django_spire:metric:visual:page:detail', kwargs={'pk': obj.pk})

    def result_name(self, obj: models.Visual) -> str:
        return obj.name

    def result_description(self, obj: models.Visual) -> str:
        statistic = (
            f'{obj.statistic.group.domain.name} / {obj.statistic.name}'
            if obj.statistic_id
            else 'No statistic'
        )

        kind = obj.get_kind_display()


        return f'{kind} - {obj.statistic.group.name} - {obj.statistic.name} - {obj.description}'
