from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


class HelpDeskTicketQuerySetTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.ticket1 = create_test_helpdesk_ticket(description='Ticket 1')
        self.ticket2 = create_test_helpdesk_ticket(description='Ticket 2')

    def test_active_returns_non_deleted(self):
        result = HelpDeskTicket.objects.active()
        assert self.ticket1 in result
        assert self.ticket2 in result

    def test_active_excludes_deleted(self):
        self.ticket1.is_deleted = True
        self.ticket1.save()

        result = HelpDeskTicket.objects.active()
        assert self.ticket1 not in result
        assert self.ticket2 in result

    def test_active_excludes_inactive(self):
        self.ticket1.is_active = False
        self.ticket1.save()

        result = HelpDeskTicket.objects.active()
        assert self.ticket1 not in result
        assert self.ticket2 in result

    def test_order_by_created_datetime(self):
        result = list(HelpDeskTicket.objects.order_by('-created_datetime'))
        assert result[0].created_datetime >= result[1].created_datetime
