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
            reverse(viewname='django_spire:help_desk:form:form', kwargs={'pk': 0}), data=ticket_data
        )

        assert response.status_code == 200

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
                viewname='django_spire:help_desk:form:form', kwargs={'pk': test_ticket.pk}
            ),
        )

        assert response.status_code == 200

    def test_helpdesk_ticket_form_delete_view(self):
        test_ticket = create_test_helpdesk_ticket()

        response = self.client.post(
            reverse('django_spire:help_desk:form:delete', kwargs={'pk': test_ticket.pk}),
            data={'should_delete': 'on'},
        )

        assert response.status_code == 302
        test_ticket.refresh_from_db()
        assert test_ticket.is_deleted is True

    def test_helpdesk_ticket_form_create_view_invalid_data(self):
        invalid_data = {'priority': '', 'purpose': '', 'description': ''}

        response = self.client.post(
            reverse(viewname='django_spire:help_desk:form:form', kwargs={'pk': 0}),
            data=invalid_data,
        )

        assert response.status_code == 200
        assert HelpDeskTicket.objects.count() == 0
