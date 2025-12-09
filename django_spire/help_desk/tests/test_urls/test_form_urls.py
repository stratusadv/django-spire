from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


class HelpDeskFormUrlsTestCase(BaseTestCase):
    def test_helpdesk_ticket_form_create_url_path(self):
        response = self.client.get(path=reverse('django_spire:help_desk:form:create'))
        assert response.status_code == 200

    def test_helpdesk_ticket_form_update_url_path(self):
        response = self.client.get(
            path=reverse(
                'django_spire:help_desk:form:update',
                kwargs={'pk': create_test_helpdesk_ticket().pk}
            ),
        )
        assert response.status_code == 200
