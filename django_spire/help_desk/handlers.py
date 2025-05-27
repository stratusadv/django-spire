from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q

from django_spire.help_desk.factories import create_ticket_event_notifications
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.enums import TicketEventType
from django_spire.notification.choices import NotificationTypeChoices


class TicketEventNotificationHandler:
    @staticmethod
    def handle_new(ticket: HelpDeskTicket):
        event_type = TicketEventType.NEW

        developers = User.objects.filter(
            email__in=[
                admin[1]
                for admin in settings.ADMINS
            ]).all()

        for notif_type in [NotificationTypeChoices.APP, NotificationTypeChoices.EMAIL]:
            create_ticket_event_notifications(
                ticket=ticket,
                users=developers,
                notification_type=notif_type,
                event_type=event_type,
            )

        managers = User.objects.filter(
            Q(groups__permissions__codename='delete_helpdeskticket') |
            Q(is_superuser=True)).all()

        create_ticket_event_notifications(
            ticket=ticket,
            users=managers,
            notification_type=NotificationTypeChoices.APP,
            event_type=event_type,
        )