from django_spire.auth.user.models import AuthUser
from django_spire.contrib.seeding import DjangoModelSeeder

from django_spire.help_desk.models import HelpDeskTicket


class HelpDeskTicketSeeder(DjangoModelSeeder):
    cache_name = 'help_desk_ticket_seeder'
    model_class = HelpDeskTicket
    fields = {
        'id': 'exclude',
        'description': ('llm', 'Help desk ticket description for software system'),
        'created_by_id': ('custom', 'fk_random', {'model_class': AuthUser}),
        'created_datetime': (
            'custom',
            'date_time_between', {'start_date': '-30d', 'end_date': 'now'}
        ),
    }
