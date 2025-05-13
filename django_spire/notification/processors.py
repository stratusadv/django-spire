from abc import ABC, abstractmethod

from django_spire.notification.models import Notification


class BaseNotificationProcessor(ABC):
    @abstractmethod
    def process(self, notification: Notification):
        raise NotImplementedError

    @abstractmethod
    def process_list(self, notifications: list[Notification]):
        raise NotImplementedError

    @abstractmethod
    def process_all(self):
        raise NotImplementedError

    @abstractmethod
    def process_errored(self):
        raise NotImplementedError
