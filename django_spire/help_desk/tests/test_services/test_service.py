from __future__ import annotations

from unittest.mock import MagicMock, patch

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.choices import (
    HelpDeskTicketPriorityChoices,
    HelpDeskTicketPurposeChoices,
    HelpDeskTicketStatusChoices,
)
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


class HelpDeskTicketServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.ticket = create_test_helpdesk_ticket()

    def test_save_model_obj_updates_purpose(self):
        self.ticket.services.obj = self.ticket
        updated_ticket = self.ticket.services.save_model_obj(
            user=self.super_user, priority=HelpDeskTicketPurposeChoices.COMPANY
        )

        assert updated_ticket.priority == HelpDeskTicketPurposeChoices.COMPANY

    def test_save_model_obj_updates_priority(self):
        self.ticket.services.obj = self.ticket
        updated_ticket = self.ticket.services.save_model_obj(
            user=self.super_user, priority=HelpDeskTicketPriorityChoices.URGENT
        )

        assert updated_ticket.priority == HelpDeskTicketPriorityChoices.URGENT

    def test_save_model_obj_updates_status(self):
        self.ticket.services.obj = self.ticket
        updated_ticket = self.ticket.services.save_model_obj(
            user=self.super_user, status=HelpDeskTicketStatusChoices.DONE
        )

        assert updated_ticket.status == HelpDeskTicketStatusChoices.DONE

    @patch(
        'django_spire.help_desk.services.notification_service.'
        'HelpDeskTicketNotificationService.create_new_ticket_notifications'
    )
    def test_create_sets_created_by(self, _mock_notifications: MagicMock):
        ticket = HelpDeskTicket()

        created_ticket = ticket.services.save_model_obj(
            user=self.super_user,
            purpose=HelpDeskTicketPurposeChoices.APP,
            priority=HelpDeskTicketPriorityChoices.LOW,
            status=HelpDeskTicketStatusChoices.READY,
            description='Test ticket',
        )

        assert created_ticket.created_by == self.super_user

    @patch(
        'django_spire.help_desk.services.notification_service.'
        'HelpDeskTicketNotificationService.create_new_ticket_notifications'
    )
    def test_create_calls_notification_service(self, mock_notifications: MagicMock):
        ticket = HelpDeskTicket()

        ticket.services.save_model_obj(
            user=self.super_user,
            purpose=HelpDeskTicketPurposeChoices.APP,
            priority=HelpDeskTicketPriorityChoices.LOW,
            status=HelpDeskTicketStatusChoices.READY,
            description='Test ticket',
        )

        mock_notifications.assert_called_once()

    @patch(
        'django_spire.help_desk.services.notification_service.'
        'HelpDeskTicketNotificationService.create_new_ticket_notifications'
    )
    def test_create_returns_ticket(self, _mock_notifications: MagicMock):
        ticket = HelpDeskTicket()

        created_ticket = ticket.services.save_model_obj(
            user=self.super_user,
            purpose=HelpDeskTicketPurposeChoices.APP,
            priority=HelpDeskTicketPriorityChoices.LOW,
            status=HelpDeskTicketStatusChoices.READY,
            description='Test ticket',
        )

        assert created_ticket.pk is not None
        assert created_ticket.purpose == HelpDeskTicketPurposeChoices.APP
