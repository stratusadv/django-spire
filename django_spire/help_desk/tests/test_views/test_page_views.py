from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


class HelpDeskPageViewsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.test_ticket = create_test_helpdesk_ticket()

    def test_ticket_delete_view(self):
        response = self.client.post(
            reverse(
                'django_spire:help_desk:page:delete',
                kwargs={'pk': self.test_ticket.pk}
            ),
            data={'should_delete': 'on'},
        )

        assert response.status_code == 302
        self.test_ticket.refresh_from_db()
        assert self.test_ticket.is_deleted is True

    def test_ticket_detail_view(self):
        response = self.client.get(
            reverse(
                'django_spire:help_desk:page:detail',
                kwargs={'pk': self.test_ticket.pk}
            ),
        )

        assert response.status_code == 200
        assert response.context_data['ticket'] == self.test_ticket

    def test_ticket_list_view(self):
        tickets = [create_test_helpdesk_ticket() for _ in range(5)]

        response = self.client.get(
            reverse('django_spire:help_desk:page:list'),
        )

        assert response.status_code == 200
        for ticket in tickets:
            assert ticket in response.context_data['tickets']

    def test_ticket_list_view_excludes_deleted(self):
        deleted_ticket = create_test_helpdesk_ticket()
        deleted_ticket.is_deleted = True
        deleted_ticket.save()

        response = self.client.get(
            reverse('django_spire:help_desk:page:list'),
        )

        assert deleted_ticket not in response.context_data['tickets']

    def test_ticket_list_view_ordered_by_created_datetime_desc(self):
        response = self.client.get(
            reverse('django_spire:help_desk:page:list'),
        )

        tickets = list(response.context_data['tickets'])
        if len(tickets) > 1:
            for i in range(len(tickets) - 1):
                assert tickets[i].created_datetime >= tickets[i + 1].created_datetime
