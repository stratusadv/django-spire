from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase

from test_project.app.task.seeding.seeder import TaskModelSeeder
from test_project.app.task.tests.factories import create_test_task


class TaskListFilteringTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        TaskModelSeeder(count=20, verbose=False).seed_database()
        create_test_task(name='Buy Eggs')
        create_test_task(name='Cook Eggs')
        create_test_task(name='Sell Eggs')

        self.data = {'name': '', 'status': ''}

    def test_task(self):
        url = reverse('task:page:list')
        response = self.client.get(
            f'{url}?session_filter_key=task_list_filter&search_value=&name=&status=com'
        )
        assert response.status_code == 200
