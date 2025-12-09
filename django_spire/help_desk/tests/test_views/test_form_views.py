from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.tests.factories import (
    create_test_helpdesk_ticket,
    create_test_helpdesk_ticket_data,
)


class HelpDeskFormViewsTestCase(BaseTestCase):
    def test_helpdesk_ticket_form_create_view(self):
        ticket_data = create_test_helpdesk_ticket_data()

        response = self.client.post(
            reverse('django_spire:help_desk:form:create'),
            data=ticket_data,
        )

        ticket = HelpDeskTicket.objects.first()

        assert response.status_code == 302
        assert response.url == reverse('django_spire:help_desk:page:list')

        assert ticket.priority == ticket_data['priority']
        assert ticket.purpose == ticket_data['purpose']
        assert ticket.status == ticket_data['status']
        assert ticket.description == ticket_data['description']

    def test_helpdesk_ticket_form_update_view(self):
        test_ticket = create_test_helpdesk_ticket()

        updated_ticket_data = create_test_helpdesk_ticket_data(
            priority='high',
            purpose='comp',
            status='prog',
            description='This is an updated test ticket.',
        )

        response = self.client.post(
            data=updated_ticket_data,
            path=reverse(
                'django_spire:help_desk:form:update',
                kwargs={'pk': test_ticket.pk}
            ),
        )

        assert response.status_code == 302
        assert response.url == reverse('django_spire:help_desk:page:list')

        test_ticket.refresh_from_db()
        assert test_ticket.priority == updated_ticket_data['priority']
        assert test_ticket.purpose == updated_ticket_data['purpose']
        assert test_ticket.status == updated_ticket_data['status']
        assert test_ticket.description == updated_ticket_data['description']

    def test_helpdesk_ticket_form_create_view_invalid_data(self):
        invalid_data = {
            'priority': '',
            'purpose': '',
            'description': '',
        }

        response = self.client.post(
            reverse('django_spire:help_desk:form:create'),
            data=invalid_data,
        )

        assert response.status_code == 200
        assert HelpDeskTicket.objects.count() == 0

    def test_helpdesk_ticket_form_create_view_sets_created_by(self):
        ticket_data = create_test_helpdesk_ticket_data()

        self.client.post(
            reverse('django_spire:help_desk:form:create'),
            data=ticket_data,
        )

        ticket = HelpDeskTicket.objects.first()
        assert ticket.created_by == self.super_user
