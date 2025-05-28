from typing import List

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q, QuerySet
from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.notifications.handlers import TicketEventNotificationHandler
from django_spire.help_desk.tests.factories import create_helpdesk_ticket
from django_spire.notification.app.models import AppNotification
from django_spire.notification.email.models import EmailNotification


TEST_ADMINS = [
    ('developer1', 'developer1@stratus.com'),
    ('developer2', 'developer2@stratus.com'),
]


class TicketEventNotificationsHandlerTestCase(BaseTestCase):
    def _assert_user_notification_ticket_integrity(
            self,
            ticket: HelpDeskTicket,
            notifications: List[EmailNotification | AppNotification],
            users: QuerySet[User]):
        self.assertEqual(len(notifications), len(users))
        for notification in notifications:
            self.assertEqual(notification.notification.content_object, ticket)
            self.assertTrue(users.filter(pk=notification.notification.user.pk).exists())

    @override_settings()
    def test_handle_new(self):
        settings.ADMINS = TEST_ADMINS

        for admin in settings.ADMINS:
            User.objects.create_user(username=admin[0], email=admin[1], password='password')

        developers = User.objects.filter(Q(email__in=[admin[1] for admin in settings.ADMINS])).all()

        managers = User.objects.filter(
            Q(groups__permissions__codename='delete_helpdeskticket') |
            Q(is_superuser=True)).all()

        ticket = create_helpdesk_ticket()
        TicketEventNotificationHandler.handle_new(ticket=ticket)

        self._assert_user_notification_ticket_integrity(
            ticket=ticket,
            notifications=AppNotification.objects.filter(notification__user__in=managers).all(),
            users=managers)

        self._assert_user_notification_ticket_integrity(
            ticket=ticket,
            notifications=EmailNotification.objects.filter(notification__user__in=developers).all(),
            users=developers)