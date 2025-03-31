from __future__ import annotations
from abc import ABC, abstractmethod
from typing_extensions import Any, TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

from django_spire.notification.models import Notification
from django_spire.notification.enums import NotificationTypeChoices
from django_spire.notification.app.models import AppNotification
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.sms.models import SmsNotification
from django_spire.notification.push.models import PushNotification

if TYPE_CHECKING:
    from django.db import models
    from django.contrib.auth.models import User


class BaseNotificationFactory(ABC):
    def __init__(self, title: str, body: str | None = None, url: str | None = None):
        self.title = title
        self.body = body
        self.url = url


    def create_notification(self, notification_type: NotificationTypeChoices) -> Notification:
        return Notification.objects.create(
                title=self.title,
                body=self.body,
                url=self.url,
                type=notification_type
            )

    @abstractmethod
    def create_email_notification(self, email: str) -> EmailNotification:
        # Abstract method for sending notification by Email
        pass

    @abstractmethod
    def create_app_notification(self, model_object: Any[models.Model]) -> AppNotification:
        # Abstract method for creating in-app notification linked to a model object
        pass

    # TODO: Implementation & Testing
    # @abstractmethod
    # def create_push_notification(self) -> PushNotification:
    #     # Abstract method for sending push notifications in a PWA
    #     pass

    # TODO: Implementation & Testing
    # @abstractmethod
    # def create_sms_notification(self, phone_number: str) -> SmsNotification:
    #     # Abstract method for sending SMS notifications
    #     pass

class NotificationFactory(BaseNotificationFactory):
    def create_email_notification(self, email: str) -> EmailNotification:
        notification = self.create_notification(NotificationTypeChoices.EMAIL)

        return EmailNotification.objects.create(
            notification=notification,
            subject=self.title,
            email=email
        )

    def create_app_notification(
        self,
        user: Any[User],
        model_object: Any[models.Model],
        url: str|None = None
    ) -> AppNotification:

        return AppNotification.objects.create(
            notification=self.create_notification(NotificationTypeChoices.APP),
            user=user,
            content_type=ContentType.objects.get_for_model(model_object),
            object_id=model_object.id,
            url=url
        )
