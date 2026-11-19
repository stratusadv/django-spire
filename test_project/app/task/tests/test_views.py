from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase

from test_project.app.task.tests.factories import create_test_task


class TaskListPageTestCase(BaseTestCase):
    def test_the_task_list_page_renders(self):
        create_test_task(name='Buy Eggs')

        response = self.client.get(reverse('task:page:list'))

        assert response.status_code == 200

    def test_a_scroll_list_served_as_a_view_fills_the_full_page_by_default(self):
        response = self.client.get(reverse('task:page:list'))

        template_names = [template.name for template in response.templates]
        assert 'django_spire/component/page/full_page.html' in template_names
