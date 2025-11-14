from __future__ import annotations

from django.contrib.auth.models import User
from django.db import models

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin

from test_project.apps.queryset_filtering.choices import TaskStatusChoices, TaskUserRoleChoices
from test_project.apps.queryset_filtering.querysets import TaskQuerySet
from test_project.apps.queryset_filtering.services.service import TaskService


class Task(ActivityMixin, HistoryModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    status = models.CharField(
        choices=TaskStatusChoices.choices,
        default=TaskStatusChoices.NEW,
        max_length=3
    )

    objects = TaskQuerySet().as_manager()
    services = TaskService()

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
        db_table = 'test_project_queryset_filtering_task'


class TaskUser(ActivityMixin, HistoryModelMixin):
    user = models.ForeignKey(
        User,
        related_name='tasks',
        related_query_name='task',
        on_delete=models.CASCADE
    )
    task = models.ForeignKey(
        Task,
        related_name='users',
        related_query_name='user',
        on_delete=models.CASCADE
    )

    role = models.CharField(
        default=TaskUserRoleChoices.LEADER,
        choices=TaskUserRoleChoices.choices,
        max_length=3
    )

    class Meta:
        verbose_name = 'Task User'
        verbose_name_plural = 'Tasks Users'
        db_table = 'test_project_queryset_filtering_task_user'
