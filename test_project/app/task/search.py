from __future__ import annotations

from django.urls import reverse

from django_spire.core.search import BaseSearch
from test_project.app.task import models


class TaskSearch(BaseSearch):
    model_class = models.Task
    searchable_fields = ['name', 'description']
    search_key = 'TASK'
    name = 'Tasks'
    icon = 'bi-list-task'

    def generate_url(self, obj: models.Task) -> str:
        return reverse('task:page:detail', kwargs={'pk': obj.pk})
