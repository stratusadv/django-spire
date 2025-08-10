from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


class HelpDeskPageViewsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.test_ticket = create_test_helpdesk_ticket()

    def test_ticket_delete_view(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:help_desk:page:delete',
                kwargs={'pk': self.test_ticket.pk}
            ),
            data={'should_delete': 'on'},
        )

        self.assertEqual(response.status_code, 302)
        self.test_ticket.refresh_from_db()
        self.assertTrue(self.test_ticket.is_deleted)

    def test_ticket_detail_view(self) -> None:
        response = self.client.get(
            reverse(
                'django_spire:help_desk:page:detail',
                kwargs={'pk': self.test_ticket.pk}
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['ticket'], self.test_ticket)

    def test_ticket_list_view(self) -> None:
        tickets = [create_test_helpdesk_ticket() for _ in range(5)]

        response = self.client.get(
            reverse('django_spire:help_desk:page:list'),
        )

        self.assertEqual(response.status_code, 200)
        for ticket in tickets:
            self.assertIn(ticket, response.context_data['tickets'])
