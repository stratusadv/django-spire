from django.db import models

from django_spire.auth.user.models import AuthUser
from django_spire.history.mixins import HistoryModelMixin

from . import choices


class HelpDeskTicket(HistoryModelMixin):
    created_by = models.ForeignKey(
        AuthUser,
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
        choices=choices.HelpDeskTicketStatusChoices.choices
    )
    description = models.TextField()

    def __str__(self):
        return f'Ticket - {self.pk}'

    class Meta:
        db_table = 'django_spire_help_desk_ticket'
        verbose_name = 'Help Desk Ticket'
        verbose_name_plural = 'Help Desk Tickets'
