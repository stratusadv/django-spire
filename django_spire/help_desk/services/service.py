from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.help_desk.services.notification_service import HelpDeskTicketNotificationService

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from django_spire.help_desk.models import HelpDeskTicket


class HelpDeskTicketService(BaseDjangoModelService['HelpDeskTicket']):
    obj: HelpDeskTicket

    notification: HelpDeskTicketNotificationService = HelpDeskTicketNotificationService()

    def save_model_obj(self, user: User, **field_data: dict) -> HelpDeskTicket:
        obj, _created = super().save_model_obj(created_by=user, **field_data)


        self.obj.services.notification.create_new_ticket_notifications()

        return obj
