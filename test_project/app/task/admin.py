from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.app.task.models import Task, TaskUser


@admin.register(Task)
class TaskAdmin(SpireModelAdmin):
    model_class = Task


@admin.register(TaskUser)
class TaskUserAdmin(SpireModelAdmin):
    model_class = TaskUser
