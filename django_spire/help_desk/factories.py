from typing import List

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.urls import reverse

from django_spire.help_desk.enums import TicketEventType
from django_spire.help_desk.exceptions import TicketEventNotificationTypeNotSupportedError
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.maps import NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP
from django_spire.notification.models import Notification


def get_ticket_event_notification_title(event_type: TicketEventType):
    content_map = {
        TicketEventType.NEW: "A new help desk ticket has been created",
    }

    return content_map[event_type]


def get_ticket_event_notification_body(event_type: TicketEventType, notification_type: NotificationTypeChoices, ticket: HelpDeskTicket):
    content_map = {
        TicketEventType.NEW: {
            NotificationTypeChoices.EMAIL: f"""
                                            <h2>A new help desk ticket (#{ticket.pk}) has been created.</h2>
                                            <p>Priority: {ticket.get_priority_display()}</p>
                                            <p>Purpose: {ticket.get_purpose_display()}</p>
                                            <p>Description:</p>
                                            <p>{ticket.description}</p>
                                        """,
            NotificationTypeChoices.APP: f'Priority: {ticket.get_priority_display()} - Purpose: {ticket.get_purpose_display()}'
        }
    }

    try:
        return content_map[event_type][notification_type]
    except KeyError:
        raise TicketEventNotificationTypeNotSupportedError(f'Combination of event type and notification type not supported: Event type {event_type} - Notification type {notification_type}')


def get_ticket_notification_url(ticket: HelpDeskTicket, notification_type: NotificationTypeChoices) -> str:
    url = reverse(
        "django_spire:help_desk:page:detail",
        kwargs={"pk": ticket.pk})

    if notification_type == NotificationTypeChoices.EMAIL:
        site_host = Site.objects.get_current()
        url = f'{site_host}/{url}'

    return url


def create_ticket_event_notification_for_user(
        ticket: HelpDeskTicket,
        notification_type: NotificationTypeChoices,
        body: str,
        title: str,
        url: str,
        user: User,
    ):
    base_notification = Notification(
        content_type=ContentType.objects.get_for_model(ticket),
        object_id=ticket.pk,
        url=url,
        title=title,
        body=body,
        type=notification_type,
        user=user
    )

    if notification_type == NotificationTypeChoices.EMAIL:
        return EmailNotification(notification=base_notification,
                                 to_email_address=user.email)
    elif notification_type == NotificationTypeChoices.APP:
        return AppNotification(notification=base_notification)
    else:
        raise TicketEventNotificationTypeNotSupportedError(notification_type)


def create_ticket_event_notifications(
        ticket: HelpDeskTicket,
        users: List[User],
        notification_type: NotificationTypeChoices,
        event_type: TicketEventType):

    title = get_ticket_event_notification_title(event_type)
    body = get_ticket_event_notification_body(event_type, notification_type, ticket)
    url = get_ticket_notification_url(ticket, notification_type)

    notifications = [
        create_ticket_event_notification_for_user(
            ticket=ticket,
            notification_type=notification_type,
            body=body,
            title=title,
            url=url,
            user=user)
        for user in users
    ]

    Notification.objects.bulk_create([notification.notification for notification in notifications if notification])
    NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP[notification_type].objects.bulk_create(notifications)