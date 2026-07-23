from django_spire.auth.user.models import AuthUser
from django_spire.contrib.seeding import Seeder
from django_spire.help_desk.choices import (
    HelpDeskTicketPriorityChoices,
    HelpDeskTicketPurposeChoices,
    HelpDeskTicketStatusChoices,
)
from django_spire.help_desk.models import HelpDeskTicket


class HelpDeskTicketSeeder(Seeder):
    model_class = HelpDeskTicket

    fields_seeds = {
        'id': Seeder.exclude(),
        'description': Seeder.llm(str),
        'purpose': Seeder.model.random_field_choice(HelpDeskTicketPurposeChoices),
        'priority': Seeder.model.random_field_choice(HelpDeskTicketPriorityChoices),
        'status': Seeder.model.random_field_choice(HelpDeskTicketStatusChoices),
        'created_by_id': Seeder.model.random_foreign_key(AuthUser),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
    }
