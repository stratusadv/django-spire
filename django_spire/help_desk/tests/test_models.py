from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.choices import (
    HelpDeskTicketPriorityChoices,
    HelpDeskTicketPurposeChoices,
    HelpDeskTicketStatusChoices,
)
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


class HelpDeskTicketModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.ticket = create_test_helpdesk_ticket()

    def test_str(self):
        assert str(self.ticket) == f'Ticket #{self.ticket.pk}'

    def test_default_status_is_ready(self):
        assert self.ticket.status == HelpDeskTicketStatusChoices.READY

    def test_get_priority_display(self):
        self.ticket.priority = HelpDeskTicketPriorityChoices.LOW
        assert self.ticket.get_priority_display() == 'Low'

        self.ticket.priority = HelpDeskTicketPriorityChoices.MEDIUM
        assert self.ticket.get_priority_display() == 'Medium'

        self.ticket.priority = HelpDeskTicketPriorityChoices.HIGH
        assert self.ticket.get_priority_display() == 'High'

        self.ticket.priority = HelpDeskTicketPriorityChoices.URGENT
        assert self.ticket.get_priority_display() == 'Urgent'

    def test_get_purpose_display(self):
        self.ticket.purpose = HelpDeskTicketPurposeChoices.APP
        assert self.ticket.get_purpose_display() == 'App'

        self.ticket.purpose = HelpDeskTicketPurposeChoices.COMPANY
        assert self.ticket.get_purpose_display() == 'Company'

    def test_get_status_display(self):
        self.ticket.status = HelpDeskTicketStatusChoices.READY
        assert self.ticket.get_status_display() == 'Ready'

        self.ticket.status = HelpDeskTicketStatusChoices.INPROGRESS
        assert self.ticket.get_status_display() == 'In Progress'

        self.ticket.status = HelpDeskTicketStatusChoices.DONE
        assert self.ticket.get_status_display() == 'Done'

    def test_created_by_relationship(self):
        assert self.ticket.created_by is not None
        assert self.ticket.created_by.pk is not None

    def test_created_datetime_auto_set(self):
        assert self.ticket.created_datetime is not None
