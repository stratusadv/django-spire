from __future__ import annotations

from test_project.app.help_desk.seeding.seeder import HelpDeskTicketSeeder


help_desk_ticket_seeder = HelpDeskTicketSeeder(count=5)

help_desk_ticket_seeder.seed_database()
