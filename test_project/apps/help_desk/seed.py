from django.utils import timezone
from django.contrib.auth.models import User

from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.choices import HelpDeskTicketPurposeChoices, HelpDeskTicketPriorityChoices

user = User.objects.get(username='stratus')

HelpDeskTicket.objects.all().delete()

help_desk_data = [
    {
        "purpose": HelpDeskTicketPurposeChoices.APP,
        "priority": HelpDeskTicketPriorityChoices.URGENT,
        "description": "This is a test urgent help desk ticket for an APP."
    },
    {
        "purpose": HelpDeskTicketPurposeChoices.COMPANY,
        "priority": HelpDeskTicketPriorityChoices.LOW,
        "description": "This is a test low priority help desk ticket for a COMPANY that was created a day ago.",
        "created_datetime": timezone.now() - timezone.timedelta(days=1)
    }
]

for data in help_desk_data:
    ticket = HelpDeskTicket.objects.create(
        created_by=user,
        purpose=data["purpose"],
        priority=data["priority"],
        description=data["description"],
    )

    if "created_datetime" in data:
        ticket.created_datetime = data["created_datetime"]
        ticket.save()
