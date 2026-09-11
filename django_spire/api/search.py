from __future__ import annotations

from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse

from django_spire.core.search import Search
from django_spire.api import models


class ApiAccessSearch(Search):
    model_class = models.ApiAccess
    searchable_fields = ['name', 'user__email', 'user__first_name', 'user__last_name']
    name = 'API Accesss'
    icon = 'bi-key'
    permission_required = 'django_spire_api.view_apiaccess'

    searchable_commands = [
        Search.Command(
            name='New API Access',
            icon='bi-plus-lg',
            url=reverse('django_spire:api:form:create'),
            action=Search.Command.Action.OPEN_URL_CURRENT_TAB,
            description='Create a new API access',
            permission_required='django_spire_api.add_apiaccess',
        )
    ]

    def base_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model_class.objects.active().select_related('user')

    def generate_list_url(self) -> str:
        return reverse('django_spire:api:page:list')

    def generate_detail_url(self, obj: models.ApiAccess) -> str:
        return reverse('django_spire:api:page:detail', kwargs={'pk': obj.pk})

    def result_name(self, obj: models.ApiAccess) -> str:
        return obj.name

    def result_description(self, obj: models.ApiAccess) -> str:
        permission = obj.get_permission_display()
        full_name = obj.user.get_full_name()

        return f'{permission} - {full_name} - {obj.user.email}'
