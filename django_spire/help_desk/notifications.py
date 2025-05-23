from typing import List

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db.models import Q, QuerySet
from django.urls import reverse

from django_spire.help_desk.exceptions import HelpDeskNotificationTypeNotSupportedError
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.maps import NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP
from django_spire.notification.models import Notification


class HelpDeskTicketNotifications:
    ticket: HelpDeskTicket

    def __init__(self, ticket: HelpDeskTicket):
        self.ticket = ticket

    # Private Helper Methods
    def _get_ticket_detail_url(self) -> str:
        site_host = Site.objects.get_current()
        site_path = reverse(
            "django_spire:help_desk:page:detail",
            kwargs={"pk": self.ticket.pk})

        return f'{site_host}/{site_path}'

    @staticmethod
    def _get_helpdesk_notification_management_users(self) -> QuerySet[User]:
        return User.objects.filter(
            Q(groups__permissions__codename='delete_helpdeskticket') |
            Q(is_superuser=True)).all()

    @staticmethod
    def _get_helpdesk_notification_developer_users(self) -> List[User]:
        developer_users_in_database = User.objects.filter(
            email__in=[
                d['email']
                for d in settings.DJANGO_SPIRE_HELPDESK_DEVELOPERS
            ]).all()

        developer_users = [
            d if d not in developer_users_in_database
            else developer_users_in_database.get(email=d['email'])
            for d in settings.DJANGO_SPIRE_HELPDESK_DEVELOPERS
        ]

        return developer_users

    def _create_helpdesk_notification_for_user(
            self,
            notification_type: NotificationTypeChoices,
            user: User | dict,
            title: str,
            body: str):
        # Handle the case where the user was not passed as a User object
        # (this means they aren't a user in the database)
        if not isinstance(user, User):
            if 'email' in user:
                user_email = user['email']
                user = None
            else:
                raise ValueError("""
                No valid user email address found for email notification recipient. 
                Ensure all the configured help desk email notification recipients have an email address.""")
        else:
            user_email = user.email

        base_notification = Notification(
            content_type=ContentType.objects.get_for_model(self.ticket),
            object_id=self.ticket.pk,
            url=self._get_ticket_detail_url(),
            title=title,
            body=body,
            type=notification_type,
            user=user
        )

        if notification_type == NotificationTypeChoices.EMAIL:
            return EmailNotification(notification=base_notification, to_email_address=user_email)

        elif notification_type == NotificationTypeChoices.APP:
            return AppNotification(notification=base_notification)

        else:
            raise HelpDeskNotificationTypeNotSupportedError(notification_type)

    def _create_helpdesk_notification_for_users(
            self,
            notification_type: NotificationTypeChoices,
            users: List[User | dict],
            title: str =None,
            body: str =None
    ):
        notifications = [
            self._create_helpdesk_notification_for_user(notification_type, user, title, body)
            for user in users
        ]

        Notification.objects.bulk_create(list(map(lambda x: x.notification, notifications)))
        NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP[notification_type].objects.bulk_create(notifications)

    # Public Methods
    def send_ticket_created_notifications(self):
        title = f'New Help Desk Ticket #{self.ticket.pk} has been created.'
        body = f"""
                    <h2>A new help desk ticket (#{self.ticket.pk}) has been created.</h2>
                    <p>Priority: {self.ticket.get_priority_display()}</p>
                    <p>Purpose: {self.ticket.get_purpose_display()}</p>
                    <p>Description:</p>
                    <p>{self.ticket.description}</p>
                """

        # Send email notifications to developers
        self._create_helpdesk_notification_for_users(
            notification_type=NotificationTypeChoices.EMAIL,
            users=self._get_helpdesk_notification_developer_users(self),
            title=title,
            body=body,
        )

        # Send app notifications to management
        app_notif_body = f'Priority: {self.ticket.get_priority_display()} - Purpose: {self.ticket.get_purpose_display()}'
        self._create_helpdesk_notification_for_users(
            notification_type=NotificationTypeChoices.APP,
            users=self._get_helpdesk_notification_management_users(self),
            title=title,
            body=app_notif_body,
        )

    def send_helpdesk_closed_notifications(self, title: str, body: str, url: str, to_email: str, publish_datetime=None):
        # TODO: Implement logic for sending closed notifications with different title and body
        raise NotImplementedError

    def send_helpdesk_comment_notifications(self, title: str, body: str, url: str, to_email: str, publish_datetime=None):
        # TODO: Implement logic for sending comment notifications with different title and body
        raise NotImplementedError