from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


class HelpDeskPageUrlsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.test_ticket = create_test_helpdesk_ticket()

    def test_ticket_delete_view_url_path(self):
        response = self.client.get(
            path=reverse(
                'django_spire:help_desk:page:delete',
                kwargs={'pk': self.test_ticket.pk}
            ),
        )
        assert response.status_code == 200

    def test_ticket_detail_view_url_path(self):
        response = self.client.get(
            path=reverse(
                'django_spire:help_desk:page:detail',
                kwargs={'pk': self.test_ticket.pk}
            ),
        )
        assert response.status_code == 200

    def test_ticket_list_view_url_path(self):
        response = self.client.get(path=reverse('django_spire:help_desk:page:list'))
        assert response.status_code == 200
