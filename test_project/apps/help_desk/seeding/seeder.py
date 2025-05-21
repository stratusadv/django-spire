from django.contrib.auth.models import User

from django_spire.contrib.seeding import DjangoModelSeeder

from django_spire.help_desk.models import HelpDeskTicket


class HelpDeskTicketSeeder(DjangoModelSeeder):
    cache_name = 'help_desk_ticket_seeder'

    model_class = HelpDeskTicket
    fields = {
        'description': ('llm', 'Help desk ticket description for software system'),
        'id': 'exclude',
        'created_by_id': ('custom', 'fk_random', {'model_class': User}),
    }

    default_to = 'faker'

