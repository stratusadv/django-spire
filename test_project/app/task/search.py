from __future__ import annotations

from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse

from django_spire.core.search import Search
from test_project.app.task import models


class TaskSearch(Search):
    model_class = models.Task
    searchable_fields = ['name', 'description']
    search_key = 'TASK'
    name = 'Tasks'
    icon = 'bi-list-task'

    searchable_commands = [
        Search.Command(
            name='New Task',
            icon='bi-plus-lg',
            url=reverse('task:modal:form', kwargs={'pk': 0}),
            action=Search.Command.Action.DISPATCH_MODAL,
            description='Create a new task',
            permission_required='test_project_task.add_task',
        )
    ]

    def base_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model_class.objects.active().filter(user__user=request.user)

    def generate_list_url(self) -> str:
        return reverse('task:page:list')

    def generate_detail_url(self, obj: models.Task) -> str:
        return reverse('task:page:detail', kwargs={'pk': obj.pk})

    def result_name(self, obj: models.Task) -> str:
        return obj.name

    def result_description(self, obj: models.Task) -> str:
        return obj.description

