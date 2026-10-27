from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase

from test_project.app.task.tests.factories import create_test_task


class TaskListPageTestCase(BaseTestCase):
    def test_the_task_list_page_renders(self):
        create_test_task(name='Buy Eggs')

        response = self.client.get(reverse('task:page:list'))

        assert response.status_code == 200
