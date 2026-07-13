from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_glue.access.access import GlueAccess
from test_project.app.task.services.factory_service import TaskFactoryService

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from test_project.app.task.models import Task


class TaskService(BaseDjangoModelService['Task']):
    obj: Task

    factory = TaskFactoryService()

    def save_model_obj(self, user: User, **field_data: dict) -> Task:
        obj, created = super().save_model_obj(**field_data)

        verb = 'created' if created else 'updated'

        obj.add_activity(
            user=user, verb=verb, information=f'{user.get_full_name()} {verb} task {obj.name}.'
        )

        return obj

    class GlueMeta:
        attributes = [
            ('factory', GlueAccess.VIEW),
        ]
