from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.tests.factories import create_helpdesk_ticket, create_helpdesk_ticket_data


class HelpDeskFormViewsTestCase(BaseTestCase):
    def test_helpdesk_ticket_form_create_view(self) -> None:
        ticket_data = create_helpdesk_ticket_data()

        response = self.client.post(
            data=ticket_data,
            path=reverse('django_spire:help_desk:form:create'),
        )

        ticket = HelpDeskTicket.objects.first()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('django_spire:help_desk:page:list'))

        self.assertEqual(ticket.priority, ticket_data['priority'])
        self.assertEqual(ticket.purpose, ticket_data['purpose'])
        self.assertEqual(ticket.status, ticket_data['status'])
        self.assertEqual(ticket.description, ticket_data['description'])


    def test_helpdesk_ticket_form_delete_view(self) -> None:
        ticket_pk = create_helpdesk_ticket().pk

        response = self.client.post(
            data={'should_delete': 'on'},
            path=reverse('django_spire:help_desk:form:delete', kwargs={'pk': ticket_pk}),
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(HelpDeskTicket.objects.get(pk=ticket_pk).is_deleted)


    def test_helpdesk_ticket_form_update_view(self) -> None:
        ticket_pk = create_helpdesk_ticket().pk

        updated_ticket_data = create_helpdesk_ticket_data(
            priority='high',
            purpose='comp',
            status='prog',
            description='This is an updated test ticket.',
        )

        response = self.client.post(
            data=updated_ticket_data,
            path=reverse('django_spire:help_desk:form:update', kwargs={'pk': ticket_pk}),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('django_spire:help_desk:page:list'))
        ticket = HelpDeskTicket.objects.get(pk=ticket_pk)
        self.assertEqual(ticket.priority, updated_ticket_data['priority'])
        self.assertEqual(ticket.purpose, updated_ticket_data['purpose'])
        self.assertEqual(ticket.status, updated_ticket_data['status'])
        self.assertEqual(ticket.description, updated_ticket_data['description'])