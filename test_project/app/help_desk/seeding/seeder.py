import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

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
    cache_enabled = True

    fields_seeds = {
        'id': Seeder.exclude(),
        'description': Seeder.llm(str),
        'purpose': Seeder.model.random_field_choice(HelpDeskTicketPurposeChoices),
        'priority': Seeder.model.random_field_choice(HelpDeskTicketPriorityChoices),
        'status': Seeder.model.random_field_choice(HelpDeskTicketStatusChoices),
        'created_by_id': Seeder.model.random_foreign_key(AuthUser),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
    }


help_desk_ticket_seeder = HelpDeskTicketSeeder(count=5)

help_desk_ticket_seeder.seed_database()
