from __future__ import annotations

from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse

from django_spire.core.search import Search
from django_spire.metric.domain import models


class DomainSearch(Search):
    model_class = models.Domain
    searchable_fields = ['name', 'description', 'sub_domain_name']
    name = 'Domains'
    icon = 'bi-collection'
    permission_required = 'django_spire_metric_domain.view_domain'

    searchable_commands = [
        Search.Command(
            name='New Domain',
            icon='bi-plus-lg',
            url=reverse('django_spire:metric:domain:form:form', kwargs={'pk': 0}),
            action=Search.Command.Action.OPEN_URL_CURRENT_TAB,
            description='Create a new domain',
            permission_required='django_spire_metric_domain.add_domain',
        )
    ]

    def base_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model_class.objects.not_deleted()

    def generate_list_url(self) -> str:
        return reverse('django_spire:metric:domain:page:list')

    def generate_detail_url(self, obj: models.Domain) -> str:
        return reverse('django_spire:metric:domain:page:detail', kwargs={'pk': obj.pk})

    def result_name(self, obj: models.Domain) -> str:
        return obj.name

    def result_description(self, obj: models.Domain) -> str:
        return f'{obj.sub_domain_name} - {obj.description}'


class SubDomainSearch(Search):
    model_class = models.SubDomain
    searchable_fields = ['name', 'description', 'domain__sub_domain_name']
    name = 'Sub Domains'
    icon = 'bi-collection'
    permission_required = 'django_spire_metric_domain.view_subdomain'

    def base_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model_class.objects.not_deleted()

    def generate_list_url(self) -> str:
        return None

    def generate_detail_url(self, obj: models.SubDomain) -> str:
        return reverse('django_spire:metric:domain:page:subdomain_detail',
                       kwargs={'domain_pk': obj.domain.pk, 'pk': obj.pk})

    def result_name(self, obj: models.SubDomain) -> str:
        return obj.name

    def result_description(self, obj: models.SubDomain) -> str:
        return f'{obj.domain.name} - {obj.domain.sub_domain_name} - {obj.description}'
