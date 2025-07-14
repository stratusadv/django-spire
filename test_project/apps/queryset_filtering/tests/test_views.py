from django.test import TestCase
from django.urls import reverse

from test_project.apps.queryset_filtering.seeding.seeder import TaskModelSeeder
from test_project.apps.queryset_filtering.tests.factories import create_test_task


class TaskListFilteringTestCase(TestCase):

    def setUp(self):
        TaskModelSeeder.seed_database(count=20)
        create_test_task(name='Buy Eggs')
        create_test_task(name='Cook Eggs')
        create_test_task(name='Sell Eggs')

        self.data = {
            'name': '',
            'status': ''
        }

    def test_queryset_filtering(self):
        url = reverse('queryset_filtering:page:list')
        response = self.client.get(f'{url}?session_filter_key=task_list_filter&search_value=&name=&status=com')
        self.assertEqual(response.status_code, 200)

