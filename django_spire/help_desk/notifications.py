from re import match
from typing import List

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.urls import reverse



from django_spire.help_desk.exceptions import HelpDeskNotificationTypeNotSupportedError
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.models import Notification
from django_spire.notification.app.models import AppNotification
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.maps import NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP
from django_spire.notification.processors.notification import NotificationProcessor


class HelpDeskTicketNotifications:
    ticket: HelpDeskTicket

    def __init__(self, ticket: HelpDeskTicket):
        self.ticket = ticket

    def _create_helpdesk_notification_for_user(
            self,
            notification_type: NotificationTypeChoices,
            user: User,
            title: str =None,
            body: str =None,
            url: str =None
    ):
        base_notification = Notification(
            content_type=ContentType.objects.get_for_model(self.ticket),
            object_id=self.ticket.pk,
            url=url,
            title=title,
            body=body,
            type=notification_type,
            user=user
        )

        if notification_type == NotificationTypeChoices.EMAIL:
            return EmailNotification(notification=base_notification, to_email_address=user.email)

        elif notification_type == NotificationTypeChoices.APP:
            return AppNotification(notification=base_notification)

        else:
            raise HelpDeskNotificationTypeNotSupportedError(notification_type)

    def _create_helpdesk_notification_for_users(
            self,
            notification_type: NotificationTypeChoices,
            users: List[User],
            title: str =None,
            body: str =None,
            url: str =None
    ):
        notifications = [
            self._create_helpdesk_notification_for_user(notification_type, user, title, body, url)
            for user in users
        ]

        test = Notification.objects.bulk_create(list(map(lambda x: x.notification, notifications)))
        NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP[notification_type].objects.bulk_create(notifications)

    def send_ticket_created_notifications(self, title:str=None, body:str=None, url:str=None):
        if title is None:
            title = f'New Help Desk Ticket #{self.ticket.pk} has been created.'

        if body is None:
            body = (
                # f'A new help desk ticket (#{self.ticket.pk}) has been created.'
                # f'\n\nPurpose: {self.ticket.purpose}'
                # f'\n\nPriority: {self.ticket.priority}'
                # f'\n\nDescription: {self.ticket.description}'
                '<html><h1>New Help Desk Ticket</h1><p>A new help desk ticket has been created.</p></html>'
            )

        if url is None:
            url = reverse('django_spire:help_desk:page:detail', kwargs={'pk': self.ticket.pk})

        # TODO: Find out best way to get management user accounts to send app notifications to
        # management_users = get_management_users()
        management_users = [User.objects.get(username='stratus')]
        self._create_helpdesk_notification_for_users(NotificationTypeChoices.APP, management_users, title, body, url)

        # TODO: Find out best way to get developer user accounts to send email notifications to - iterate through them and send notifs to all
        # developer_users = get_developer_users()
        developer_users = management_users
        self._create_helpdesk_notification_for_users(NotificationTypeChoices.EMAIL, developer_users, title, body, url)

    def send_helpdesk_closed_notifications(self, title: str, body: str, url: str, to_email: str, publish_datetime=None):
        # TODO: Implement logic for sending closed notifications with different title and body
        raise NotImplementedError

    def send_helpdesk_comment_notifications(self, title: str, body: str, url: str, to_email: str, publish_datetime=None):
        # TODO: Implement logic for sending comment notifications with different title and body
        raise NotImplementedError