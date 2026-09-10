from __future__ import annotations

from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse

from django_spire.core.search import Search
from django_spire.metric.domain.statistic import models


class StatisticSearch(Search):
    model_class = models.Statistic
    searchable_fields = ['name', 'interval', 'value_type', 'group__name', 'group__domain__name']
    name = 'Statistics'
    icon = 'bi-bar-chart'
    permission_required = 'django_spire_metric_domain.view_statistic'

    searchable_commands = [
        Search.Command(
            name='New Statistic',
            icon='bi-plus-lg',
            url=reverse('django_spire:metric:domain:statistic:form:create', kwargs={'group_pk': 0}),
            action=Search.Command.Action.OPEN_URL_CURRENT_TAB,
            description='Create a new statistic',
            permission_required='django_spire_metric_domain.add_statistic',
        )
    ]

    def base_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model_class.objects.not_deleted().select_related('group__domain')

    def generate_list_url(self) -> str:
        return None

    def generate_detail_url(self, obj: models.Statistic) -> str:
        return reverse('django_spire:metric:domain:statistic:page:detail', kwargs={'pk': obj.pk})

    def result_name(self, obj: models.Statistic) -> str:
        return obj.name

    def result_description(self, obj: models.Statistic) -> str:
        interval = obj.get_interval_display()
        value_type = obj.get_value_type_display()

        return f'{obj.group.name} - {interval} - {value_type} - {obj.group.domain.name}'


class StatisticGroupSearch(Search):
    model_class = models.StatisticGroup
    searchable_fields = ['name', 'description', 'domain__name', 'domain__sub_domain_name']
    name = 'Statistic Groups'
    icon = 'bi-bar-chart'
    permission_required = 'django_spire_metric_domain.view_statisticgroup'

    searchable_commands = [
        Search.Command(
            name='New Statistic Group',
            icon='bi-plus-lg',
            url=reverse('django_spire:metric:domain:statistic:form:group_create'),
            action=Search.Command.Action.OPEN_URL_CURRENT_TAB,
            description='Create a new statistic group',
            permission_required='django_spire_metric_domain.add_statisticgroup',
        )
    ]

    def base_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model_class.objects.not_deleted().select_related('domain')

    def generate_list_url(self) -> str:
        return reverse('django_spire:metric:domain:statistic:page:group_list')

    def generate_detail_url(self, obj: models.StatisticGroup) -> str:
        return reverse(
            'django_spire:metric:domain:statistic:page:group_detail', kwargs={'pk': obj.pk}
        )

    def result_name(self, obj: models.StatisticGroup) -> str:
        return obj.name

    def result_description(self, obj: models.StatisticGroup) -> str:
        return f'{obj.domain.name} - {obj.domain.sub_domain_name} - {obj.description}'
