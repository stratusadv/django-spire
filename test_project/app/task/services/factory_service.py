from __future__ import annotations

from typing import TYPE_CHECKING

from django_glue import Glue

from django_spire.contrib.constructor.service import BaseDjangoModelService
from test_project.app.task.choices import TaskStatusChoices

if TYPE_CHECKING:
    from django.http import HttpRequest
    from test_project.app.task.models import Task


class TaskFactoryService(BaseDjangoModelService['Task']):
    obj: Task

    @Glue.Attribute(access=Glue.Access.CHANGE)
    def duplicate(self, request: HttpRequest) -> dict:
        new_task = self.obj_class.services.save_model_obj(
            user=request.user,
            name=f"{self.obj.name} (Copy)",
            description=self.obj.description,
            status=TaskStatusChoices.NEW,
        )
        return {'success': True, 'new_task_id': new_task.id}
