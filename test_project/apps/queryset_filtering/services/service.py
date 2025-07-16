from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from test_project.apps.queryset_filtering.models import Task


class TaskService(BaseDjangoModelService['Task']):
    obj: Task
