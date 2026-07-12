from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.handlers.wsgi import WSGIRequest
from django_glue.bound_attributes.decorators import bind_attribute
from django_glue.access.access import GlueAccess

from django_spire.contrib.constructor.service import BaseDjangoModelService
from test_project.app.task.choices import TaskStatusChoices

if TYPE_CHECKING:
    from test_project.app.task.models import Task


class TaskFactoryService(BaseDjangoModelService['Task']):
    obj: Task

    @bind_attribute(access=GlueAccess.CHANGE)
    def duplicate(self, request: WSGIRequest) -> dict:
        new_task = self.obj_class.services.save_model_obj(
            user=request.user,
            name=f"{self.obj.name} (Copy)",
            description=self.obj.description,
            status=TaskStatusChoices.NEW,
        )
        return {'success': True, 'new_task_id': new_task.id}

    class GlueMeta:
        attributes = [
            ('duplicate', {'access': GlueAccess.CHANGE}),
        ]
