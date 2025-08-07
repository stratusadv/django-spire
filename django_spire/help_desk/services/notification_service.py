from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db.models import Q
from typing import TYPE_CHECKING

from django.urls import reverse

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.help_desk.exceptions import (
    TicketEventNotificationTypeNotSupportedError,
)
from django_spire.help_desk.enums import TicketEventType
from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.maps import NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP
from django_spire.notification.models import Notification

if TYPE_CHECKING:
    from django_spire.help_desk.models import HelpDeskTicket


class HelpDeskTicketNotificationService(BaseDjangoModelService['HelpDeskTicket']):
    obj: HelpDeskTicket

    def create_new_ticket_notifications(self):
        event_type = TicketEventType.NEW

        developers = User.objects.filter(
            email__in=[
                admin[1]
                for admin in settings.ADMINS
            ]
        )

        for notif_type in [NotificationTypeChoices.APP, NotificationTypeChoices.EMAIL]:
            self._create_ticket_event_notifications(
                users=developers,
                notification_type=notif_type,
                event_type=event_type,
            )

        managers = User.objects.filter(
            Q(groups__permissions__codename='delete_helpdeskticket')
        )

        self._create_ticket_event_notifications(
            users=managers,
            notification_type=NotificationTypeChoices.APP,
            event_type=event_type,
        )

    @staticmethod
    def _get_ticket_event_notification_title(event_type: TicketEventType) -> str:
        content_map = {
            TicketEventType.NEW: 'A new help desk ticket has been created',
        }

        return content_map[event_type]

    def _get_ticket_event_notification_body(
            self,
            event_type: TicketEventType,
            notification_type: NotificationTypeChoices,
    ) -> str:
        content_map = {
            TicketEventType.NEW: {
                NotificationTypeChoices.EMAIL: f"""
                    <h2>A new help desk ticket (#{self.obj.pk}) has been created.</h2>
                    <p>Priority: {self.obj.get_priority_display()}</p>
                    <p>Purpose: {self.obj.get_purpose_display()}</p>
                    <p>Description:</p>
                    <p>{self.obj.description}</p>
                """,
                NotificationTypeChoices.APP: (
                    f'Priority: {self.obj.get_priority_display()} - '
                    f'Purpose: {self.obj.get_purpose_display()}'
                ),
            }
        }

        try:
            return content_map[event_type][notification_type]
        except KeyError:
            raise TicketEventNotificationTypeNotSupportedError(
                f'Combination of event type and notification type not supported: '
                f'Event type {event_type} - Notification type {notification_type}'
            )

    def _get_ticket_notification_url(
            self,
            notification_type: NotificationTypeChoices
    ) -> str:
        path = reverse('django_spire:help_desk:page:detail', kwargs={'pk': self.obj.pk})

        if notification_type == NotificationTypeChoices.EMAIL:
            site_host = Site.objects.get_current()
            return f'{site_host}{path}'

        return path

    def _create_ticket_event_notification_for_user(
            self,
            notification_type: NotificationTypeChoices,
            body: str,
            title: str,
            url: str,
            user: User,
    ) -> EmailNotification | AppNotification:
        base_notification = Notification(
            content_type=ContentType.objects.get_for_model(self.obj),
            object_id=self.obj.pk,
            url=url,
            title=title,
            body=body,
            type=notification_type,
            user=user,
        )

        if notification_type == NotificationTypeChoices.EMAIL:
            return EmailNotification(
                notification=base_notification,
                to_email_address=(
                    settings.DEVELOPMENT_EMAIL if settings.DEBUG else user.email
                )
            )
        elif notification_type == NotificationTypeChoices.APP:
            return AppNotification(notification=base_notification)
        else:
            raise TicketEventNotificationTypeNotSupportedError(notification_type)

    def _create_ticket_event_notifications(
            self,
            users: list[User],
            notification_type: NotificationTypeChoices,
            event_type: TicketEventType,
    ):
        title = self._get_ticket_event_notification_title(event_type)
        body = self._get_ticket_event_notification_body(
            event_type=event_type,
            notification_type=notification_type,
        )
        url = self._get_ticket_notification_url(notification_type)

        notifications = [
            self._create_ticket_event_notification_for_user(
                notification_type=notification_type,
                body=body,
                title=title,
                url=url,
                user=user,
            )
            for user in users
        ]

        Notification.objects.bulk_create(
            [
                notification.notification
                for notification in notifications
                if notification
            ]
        )
        NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP[notification_type].objects.bulk_create(
            notifications
        )
