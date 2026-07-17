from __future__ import annotations

from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django_glue import Glue, GlueAccess

from django_spire.help_desk.choices import (
    HelpDeskTicketPriorityChoices,
    HelpDeskTicketPurposeChoices,
    HelpDeskTicketStatusChoices,
)
from django_spire.help_desk.querysets import HelpDeskTicketQuerySet
from django_spire.help_desk.services.service import HelpDeskTicketService
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin


class HelpDeskTicket(ActivityMixin, HistoryModelMixin):
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_help_desk_tickets',
        related_query_name='created_help_desk_ticket',
        editable=False,
        verbose_name='Created By',
    )
    purpose = models.CharField(
        max_length=4, choices=HelpDeskTicketPurposeChoices.choices, verbose_name='Purpose'
    )
    priority = models.CharField(
        max_length=4, choices=HelpDeskTicketPriorityChoices.choices, verbose_name='Priority'
    )
    status = models.CharField(
        max_length=4,
        choices=HelpDeskTicketStatusChoices.choices,
        default=HelpDeskTicketStatusChoices.READY,
        verbose_name='Status',
    )
    description = models.TextField()

    objects = HelpDeskTicketQuerySet.as_manager()
    services = Glue.attribute(HelpDeskTicketService(), access=Glue.Access.DELETE)

    @Glue.attribute(access=GlueAccess.CHANGE)
    def complete(self, request: WSGIRequest) -> None:
        self.status = HelpDeskTicketStatusChoices.DONE
        self.services.save_model_obj(user=request.user, obj=self, status=self.status)

    def __str__(self):
        return f'Ticket #{self.pk}'

    class Meta:
        db_table = 'django_spire_help_desk_ticket'
        verbose_name = 'Help Desk Ticket'
        verbose_name_plural = 'Help Desk Tickets'
