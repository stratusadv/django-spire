from __future__ import annotations

from django.contrib.postgres.aggregates import StringAgg
from django.db.models import CharField, OuterRef, QuerySet, Subquery, Value
from django.db.models.functions import Coalesce
from django.http import HttpRequest
from django.urls import reverse

from django_spire.core.search import Search
from django_spire.metric.visual.signage import models


class SignageSearch(Search):
    model_class = models.Signage
    searchable_fields = ['name', 'title', 'description', 'key', 'presentation_names']
    name = 'Signages'
    icon = 'bi-tv'
    permission_required = 'django_spire_metric_visual_signage.view_signage'

    searchable_commands = [
        Search.Command(
            name='New Signage',
            icon='bi-plus-lg',
            url=reverse('django_spire:metric:visual:signage:form:create'),
            action=Search.Command.Action.OPEN_URL_CURRENT_TAB,
            description='Create a new signage',
            permission_required='django_spire_metric_visual_signage.add_signage',
        )
    ]

    def base_queryset(self, request: HttpRequest) -> QuerySet:
        active_names = (
            models.SignagePresentation.objects.filter(
                signage_id=OuterRef('pk'), is_deleted=False, presentation__is_deleted=False
            )
            .values('signage_id')
            .annotate(
                names=StringAgg('presentation__name', delimiter=' ', output_field=CharField())
            )
            .values('names')
        )

        return self.model_class.objects.not_deleted().annotate(
            presentation_names=Coalesce(Subquery(active_names), Value(''), output_field=CharField())
        )

    def generate_list_url(self) -> str:
        return reverse('django_spire:metric:visual:signage:page:list')

    def generate_detail_url(self, obj: models.Signage) -> str:
        return reverse('django_spire:metric:visual:signage:page:detail', kwargs={'pk': obj.pk})

    def result_name(self, obj: models.Signage) -> str:
        return obj.name

    def result_description(self, obj: models.Signage) -> str:
        presentations = ' - '.join(
            link.presentation.name for link in obj.services.transformation.presentation_links()
        )

        return f'{f"{obj.title} - " if obj.title else ""}{presentations} - {obj.description}'
