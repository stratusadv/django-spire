from __future__ import annotations
from abc import ABC, abstractmethod
from typing_extensions import Any, TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

from django_spire.notification.models import Notification
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


    def create_notification(self) -> Notification:
        return Notification.objects.create(
                title=self.title,
                body=self.body
            )
    @abstractmethod
    def send_email(self, email: str) -> EmailNotification:
        # Abstract method for sending notification by Email
        pass

    @abstractmethod
    def in_app(self, model_object: Any[models.Model]) -> AppNotification:
        # Abstract method for creating in-app notification linked to a model object
        pass

    # TODO: Implementation & Testing
    # @abstractmethod
    # def push(self) -> PushNotification:
    #     # Abstract method for sending push notifications in a PWA
    #     pass

    # TODO: Implementation & Testing
    # @abstractmethod
    # def send_sms(self, phone_number: str) -> SmsNotification:
    #     # Abstract method for sending SMS notifications
    #     pass

class NotificationFactory(BaseNotificationFactory):
    def email_factory(self, email: str) -> EmailNotification:
        notification = self.create_notification()

        return EmailNotification.objects.create(
            notification=notification,
            subject=self.title,
            email=email
        )

    def app_factory(
        self,
        user: Any[User],
        model_object: Any[models.Model],
        url: str|None = None
    ) -> AppNotification:

        return AppNotification.objects.create(
            notification=self.create_notification(),
            user=user,
            content_type=ContentType.objects.get_for_model(model_object),
            object_id=model_object.id,
            url=url
        )
