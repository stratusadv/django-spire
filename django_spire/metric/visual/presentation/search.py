from __future__ import annotations

from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse

from django_spire.core.search import Search

from django_spire.metric.visual.presentation import models


class PresentationSearch(Search):
    model_class = models.Presentation
    searchable_fields = ['name', 'description']
    name = 'Presentations'
    icon = 'bi-easel'
    permission_required = 'django_spire_metric_visual_presentation.view_presentation'

    searchable_commands = [
        Search.Command(
            name='New Presentation',
            icon='bi-plus-lg',
            url=reverse('django_spire:metric:visual:presentation:form:create'),
            action=Search.Command.Action.OPEN_URL_CURRENT_TAB,
            description='Create a new presentation',
            permission_required='django_spire_metric_visual_presentation.add_presentation',
        )
    ]

    def base_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model_class.objects.not_deleted()

    def generate_list_url(self) -> str:
        return reverse('django_spire:metric:visual:presentation:page:list')

    def generate_detail_url(self, obj: models.Presentation) -> str:
        return reverse('django_spire:metric:visual:presentation:page:detail', kwargs={'pk': obj.pk})

    def result_name(self, obj: models.Presentation) -> str:
        return obj.name

    def result_description(self, obj: models.Presentation) -> str:
        slides = ' - '.join(slide.name for slide in obj.slides.not_deleted())

        return f'{slides} - {obj.description}'
