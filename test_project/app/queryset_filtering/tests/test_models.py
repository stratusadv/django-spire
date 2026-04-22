from __future__ import annotations

from django.test import TestCase

from test_project.apps.queryset_filtering.models import Task
from test_project.apps.queryset_filtering.tests.factories import create_test_task


class TaskModelTestCase(TestCase):
    def setUp(self):
        self.task = create_test_task()

    def test_task_creation(self):
        assert isinstance(self.task, Task)
