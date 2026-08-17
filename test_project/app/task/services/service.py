from __future__ import annotations

from typing import TYPE_CHECKING

from django_glue import Glue
from django_spire.contrib.constructor.service import BaseDjangoModelService
from test_project.app.task.services.factory_service import TaskFactoryService

if TYPE_CHECKING:
    from test_project.app.task.models import Task


class TaskService(BaseDjangoModelService['Task']):
    obj: Task

    factory = Glue.attr(TaskFactoryService(), required_access=Glue.Access.DELETE)
