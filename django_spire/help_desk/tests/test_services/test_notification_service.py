from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q, QuerySet
from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket
from django_spire.notification.app.models import AppNotification
from django_spire.notification.email.models import EmailNotification

if TYPE_CHECKING:
    from django_spire.help_desk.models import HelpDeskTicket


TEST_ADMINS = [
    ('developer1', 'developer1@stratus.com'),
    ('developer2', 'developer2@stratus.com'),
]


class HelpDeskTicketNotificationServiceTestCase(BaseTestCase):
    def _assert_user_notification_ticket_integrity(
        self,
        ticket: HelpDeskTicket,
        notification_type: type,
        users: QuerySet[User]
    ):
        notifications = notification_type.objects.by_users(users)
        assert len(notifications) == len(users)

        for notification in notifications:
            assert not notification.notification.content_object == ticket
            assert users.filter(pk=notification.notification.user.pk).exists()

    @override_settings(ADMINS=TEST_ADMINS)
    def test_create_new_ticket_notifications(self):
        for admin in settings.ADMINS:
            User.objects.create_user(username=admin[0], email=admin[1], password='password')

        developers = User.objects.filter(Q(email__in=[admin[1] for admin in settings.ADMINS]))

        managers = User.objects.filter(
            Q(groups__permissions__codename='delete_helpdeskticket')
        )

        ticket = create_test_helpdesk_ticket()
        ticket.services.notification.create_new_ticket_notifications()

        self._assert_user_notification_ticket_integrity(
            ticket=ticket,
            notification_type=AppNotification,
            users=managers
        )

        self._assert_user_notification_ticket_integrity(
            ticket=ticket,
            notification_type=AppNotification,
            users=developers
        )

        self._assert_user_notification_ticket_integrity(
            ticket=ticket,
            notification_type=EmailNotification,
            users=developers
        )
