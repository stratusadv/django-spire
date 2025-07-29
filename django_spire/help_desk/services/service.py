from __future__ import annotations
from typing import TYPE_CHECKING


from django_spire.contrib.service import BaseDjangoModelService
from django_spire.help_desk.services.notification_service import \
    HelpDeskTicketNotificationService

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django_spire.help_desk.models import HelpDeskTicket


class HelpDeskTicketService(BaseDjangoModelService['HelpDeskTicket']):
    obj: HelpDeskTicket

    notification: HelpDeskTicketNotificationService = HelpDeskTicketNotificationService()

    def create(self, created_by: User, **kwargs) -> HelpDeskTicket:
        self.obj.created_by = created_by
        _ = self.obj.services.save_model_obj(**kwargs)

        self.obj.services.notification.create_new_ticket_notifications()

        return self.obj
