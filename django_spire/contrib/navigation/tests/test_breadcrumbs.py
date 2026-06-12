from django.test import TestCase

from django_spire.contrib.navigation.breadcrumbs import Breadcrumbs

from test_project.app.task.models import Task


class TestBreadcrumbs(TestCase):
    def test_breadcrumbs_init(self):
        _ = Breadcrumbs()
        assert True

    def test_breadcrumbs_add_model(self):
        breadcrumbs = Breadcrumbs()

        breadcrumbs.add_model_name(Task)
        breadcrumbs.add_model_plural_name(Task)

        assert breadcrumbs.items[0].name == 'Task'
        assert breadcrumbs.items[1].name == 'Tasks'

        task = Task(name='Testing Task')

        breadcrumbs.add_model_instance_string(task)
        breadcrumbs.add_model_instance_form_action(task)

        assert breadcrumbs.items[2].name == 'Testing Task'
        assert breadcrumbs.items[3].name == 'Create'
