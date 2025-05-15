from django.utils import timezone
from django.contrib.auth.models import User

from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.choices import HelpDeskTicketPurposeChoices, HelpDeskTicketPriorityChoices
from test_project.apps.help_desk.seeding.seeder import HelpDeskTicketSeeder

user = User.objects.get(username='stratus')

HelpDeskTicketSeeder.seed_database(count=5)
