from __future__ import annotations

from django.contrib.auth.models import User
from django.db import models
from django.core.handlers.wsgi import WSGIRequest

from django_glue.bound_attributes.decorators import bind_attribute
from django_glue.access.access import GlueAccess

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin

from test_project.app.task.choices import TaskStatusChoices, TaskUserRoleChoices
from test_project.app.task.querysets import TaskQuerySet, TaskUserQuerySet
from test_project.app.task.services.service import TaskService


class Task(ActivityMixin, HistoryModelMixin):
    parent = models.ForeignKey(
        'self', blank=True, null=True, related_name='children', related_query_name='child', on_delete=models.CASCADE
    )

    name = models.CharField(max_length=255)

    description = models.TextField(default='')

    status = models.CharField(
        choices=TaskStatusChoices.choices, default=TaskStatusChoices.NEW, max_length=3
    )

    objects = TaskQuerySet().as_manager()
    services = TaskService()

    @bind_attribute(access=GlueAccess.CHANGE)
    def complete(self, request: WSGIRequest) -> None:
        self.status = TaskStatusChoices.DONE
        self.services.save_model_obj(user=request.user, obj=self, status=self.status)

    def __str__(self):
        return self.name

    def user_initials(self):
        return [
            f'{user_bridge.user.first_name} {user_bridge.user.id}'
            for user_bridge in self.users.all()
        ]

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        db_table = 'test_project_task_task'

    class GlueMeta:
        attributes = [('services', {'access': GlueAccess.VIEW, 'perist_state': True})]


class TaskUser(ActivityMixin, HistoryModelMixin):
    user = models.ForeignKey(
        User, related_name='tasks', related_query_name='task', on_delete=models.CASCADE
    )

    task = models.ForeignKey(
        Task, related_name='users', related_query_name='user', on_delete=models.CASCADE
    )

    role = models.CharField(
        default=TaskUserRoleChoices.LEADER, choices=TaskUserRoleChoices.choices, max_length=3
    )

    objects = TaskUserQuerySet.as_manager()

    class Meta:
        verbose_name = 'Task User'
        verbose_name_plural = 'Tasks Users'
        db_table = 'test_project_task_task_user'
