from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.tests.factories import create_helpdesk_ticket


class HelpDeskPageViewsTestCase(BaseTestCase):
    def test_helpdesk_ticket_page_list_view(self) -> None:
        tickets = [create_helpdesk_ticket() for _ in range(5)]

        response = self.client.get(
            path=reverse('django_spire:help_desk:page:list'),
        )

        self.assertEqual(response.status_code, 200)
        for ticket in tickets:
            self.assertIn(ticket, response.context_data['tickets'])

    def test_helpdesk_ticket_page_detail_view(self) -> None:
        ticket = create_helpdesk_ticket()

        response = self.client.get(
            path=reverse('django_spire:help_desk:page:detail', kwargs={'pk': ticket.pk}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['ticket'], ticket)