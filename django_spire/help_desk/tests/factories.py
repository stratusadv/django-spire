from django.contrib.auth.models import User

from django_spire.help_desk.choices import HelpDeskTicketPriorityChoices, \
    HelpDeskTicketPurposeChoices, HelpDeskTicketStatusChoices
from django_spire.help_desk.models import HelpDeskTicket


def create_helpdesk_ticket_data(**kwargs) -> dict:
    ticket_data = {
        'priority': HelpDeskTicketPriorityChoices.LOW,
        'purpose': HelpDeskTicketPurposeChoices.APP,
        'status': HelpDeskTicketStatusChoices.READY,
        'description': 'This is a test ticket.',
    }

    ticket_data.update(**kwargs)

    return ticket_data

def create_helpdesk_ticket(**kwargs):
    if 'created_by' not in kwargs:
        kwargs['created_by'] = User.objects.first()

    return HelpDeskTicket.objects.create(**create_helpdesk_ticket_data(**kwargs))
