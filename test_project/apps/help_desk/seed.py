from django.contrib.auth.models import User

from test_project.apps.help_desk.seeding.seeder import HelpDeskTicketSeeder

user = User.objects.get(username='stratus')

HelpDeskTicketSeeder.seed_database(count=5)
