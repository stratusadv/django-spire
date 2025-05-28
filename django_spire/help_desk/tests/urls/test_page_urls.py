from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.tests.factories import create_helpdesk_ticket


class HelpDeskPageUrlsTestCase(BaseTestCase):
    def test_helpdesk_ticket_page_list_url_path(self) -> None:
        response = self.client.get(
            path=reverse('django_spire:help_desk:page:list'),
        )

        self.assertEqual(response.status_code, 200)

    def test_helpdesk_ticket_page_detail_url_path(self) -> None:
        response = self.client.get(
            path=reverse('django_spire:help_desk:page:detail', kwargs={'pk': create_helpdesk_ticket().pk}),
        )

        self.assertEqual(response.status_code, 200)