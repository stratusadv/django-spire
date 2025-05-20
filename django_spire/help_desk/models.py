from django.db import models
from django.contrib.auth.models import User

from django_spire.help_desk.querysets import HelpDeskTicketQuerySet
from django_spire.history.mixins import HistoryModelMixin

from django_spire.help_desk import choices


class HelpDeskTicket(HistoryModelMixin):
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_help_desk_tickets',
        related_query_name='created_help_desk_ticket',
        editable=False,
    )
    purpose = models.CharField(
        max_length=4,
        choices=choices.HelpDeskTicketPurposeChoices.choices
    )
    priority = models.CharField(
        max_length=4,
        choices=choices.HelpDeskTicketPriorityChoices.choices
    )
    status = models.CharField(
        max_length=4,
        choices=choices.HelpDeskTicketStatusChoices.choices,
        default=choices.HelpDeskTicketStatusChoices.READY
    )
    description = models.TextField()

    objects = HelpDeskTicketQuerySet.as_manager()

    def __str__(self):
        return f'Ticket - {self.pk}'

    class Meta:
        db_table = 'django_spire_help_desk_ticket'
        verbose_name = 'Help Desk Ticket'
        verbose_name_plural = 'Help Desk Tickets'
