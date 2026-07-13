from __future__ import annotations

from typing import TYPE_CHECKING

from django_glue.access.access import GlueAccess

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.help_desk.services.notification_service import HelpDeskTicketNotificationService

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from django_spire.help_desk.models import HelpDeskTicket


class HelpDeskTicketService(BaseDjangoModelService['HelpDeskTicket']):
    obj: HelpDeskTicket

    notification: HelpDeskTicketNotificationService = HelpDeskTicketNotificationService()

    # def create(self, created_by: User, **kwargs) -> HelpDeskTicket:
    #     self.obj.created_by = created_by
    #     self.obj, _ = self.obj.services.save_model_obj(**kwargs)
    #
    #     self.obj.services.notification.create_new_ticket_notifications()
    #
    #     return self.obj

    def save_model_obj(self, user: User, **field_data: dict) -> HelpDeskTicket:
        obj, created = super().save_model_obj(**field_data)

        verb = 'created' if created else 'updated'

        obj.add_activity(
            user=user, verb=verb, information=f'{user.get_full_name()} {verb} task {obj.name}.'
        )

        return obj

    class GlueMeta:
        attributes = [
            # ('factory', GlueAccess.VIEW),
        ]
