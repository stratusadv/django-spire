from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.tests.factories import create_helpdesk_ticket


class HelpDeskUrlsTestCase(BaseTestCase):
    def test_helpdesk_ticket_form_create_url_path(self) -> None:
        response = self.client.get(
            path=reverse('django_spire:help_desk:form:create'),
        )

        self.assertEqual(response.status_code, 200)

    def test_helpdesk_ticket_form_delete_url_path(self) -> None:
        response = self.client.get(
            path=reverse('django_spire:help_desk:form:delete', kwargs={'pk': create_helpdesk_ticket().pk}),
        )

        self.assertEqual(response.status_code, 200)

    def test_helpdesk_ticket_form_update_url_path(self) -> None:
        response = self.client.get(
            path=reverse('django_spire:help_desk:form:update', kwargs={'pk': 1}),
        )

        self.assertEqual(response.status_code, 200)


