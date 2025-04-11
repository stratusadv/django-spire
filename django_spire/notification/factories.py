from __future__ import annotations
from abc import ABC, abstractmethod
from typing_extensions import Any, TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

from django_spire.notification.models import Notification
from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.app.models import AppNotification
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.sms.models import SmsNotification
from django_spire.notification.push.models import PushNotification

if TYPE_CHECKING:
    from django.db import models
    from django.contrib.auth.models import User


class BaseNotificationFactory(ABC):
    """
    Abstract base class for notification factories.

    This class serves as a blueprint for creating different types of notifications.
    Subclasses should implement specific methods to create various kinds of notifications.

    Attributes:
        model_object (Any[models.Model]): The model object associated with the notification.
        title (str): The title or main text of the notification.
        body (Optional[str]): Additional content or details of the notification. Defaults to None.
        url (Optional[str]): URL associated with the notification, if any. Defaults to None.

    """

    def __init__(self, model_object: Any[models.Model], title: str, body: str | None = None, url: str | None = None):
        self.model_object = model_object
        self.title = title
        self.body = body
        self.url = url


    def create_notification(self, notification_type: NotificationTypeChoices) -> Notification:
        """
        Method for creating base `Notification` objects.

        :param notification_type (str): The type of the notification.

        :return Notification: A new instance of the specified notification.
        """
        return Notification.objects.create(
                content_type=ContentType.objects.get_for_model(self.model_object),
                object_id=self.model_object.id,
                title=self.title,
                body=self.body,
                url=self.url,
                type=notification_type,
            )

    @abstractmethod
    def create_email_notification(self, email: str) -> EmailNotification:
        """
        Abstract method for sending notification by Email
        :param: email(str): The recipient's email address for the notification.
        :return EmailNotification: A new instance of an email notification.
        """

    @abstractmethod
    def create_app_notification(self, model_object: Any[models.Model], user: Any[User], url: str|None = None) -> AppNotification:
        """
        Abstract method for creating in-app notification linked to a model object
        :param model_object: The model object associated with the notification.
        :param user: The user who will receive the notification.
        :param url (Optional[str]): URL related to the notification, if required override to url specified in factory.
        """

    # TODO: Implementation & Testing
    # @abstractmethod
    # def create_push_notification(self) -> PushNotification:
    #     """Abstract method for sending push notifications in a PWA"""
    #     pass

    # TODO: Implementation & Testing
    # @abstractmethod
    # def create_sms_notification(self, phone_number: str) -> SmsNotification:
    #     """Abstract method for sending SMS notifications"""
    #     pass


class NotificationFactory(BaseNotificationFactory):
    """
    Concrete implementation for creating different types of notifications.

    This class provides methods to create specific types of notifications, such as email and app notifications.
    """

    def create_email_notification(self, email: str) -> EmailNotification:
        """
        Creates an email notification.
        :param email (str): The recipient's email address for the notification.
        :return EmailNotification: A new instance of an email notification.
        """

        return EmailNotification.objects.create(
            notification=self.create_notification(NotificationTypeChoices.EMAIL),
            subject=self.title,
            email=email
        )

    def create_app_notification(
        self,
        user: Any[User],
    ) -> AppNotification:
        """
        Creates an app notification.

        :param user (User): The user who will receive the notification.
        :param model_object (models.Model): The model object associated with the notification.

        :return AppNotification: A new instance of an app notification.
        """
        return AppNotification.objects.create(
            notification=self.create_notification(NotificationTypeChoices.APP),
            user=user,
        )
