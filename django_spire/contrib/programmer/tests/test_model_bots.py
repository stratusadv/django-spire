from __future__ import annotations

from django.test import TestCase

from django_spire.contrib.programmer.models import bots



model_file_data = """
from __future__ import annotations

from django.db import models
from django.contrib.auth.models import User

from django_spire.help_desk.querysets import HelpDeskTicketQuerySet
from django_spire.help_desk.services.service import HelpDeskTicketService
from django_spire.history.mixins import HistoryModelMixin

from django_spire.help_desk import choices


class HelpDeskTicket(HistoryModelMixin):
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_help_desk_tickets',
        related_query_name='created_help_desk_ticket',
        editable=False,
        verbose_name='Created By'
    )
    purpose = models.CharField(
        max_length=4,
        choices=choices.HelpDeskTicketPurposeChoices.choices,
        verbose_name='Purpose'
    )
    priority = models.CharField(
        max_length=4,
        choices=choices.HelpDeskTicketPriorityChoices.choices,
        verbose_name='Priority'
    )
    status = models.CharField(
        max_length=4,
        choices=choices.HelpDeskTicketStatusChoices.choices,
        default=choices.HelpDeskTicketStatusChoices.READY,
        verbose_name='Status'
    )
    description = models.TextField()

    objects = HelpDeskTicketQuerySet.as_manager()
    services = HelpDeskTicketService()

    def __str__(self):
        return f'Ticket #{self.pk}'

    class Meta:
        db_table = 'django_spire_help_desk_ticket'
        verbose_name = 'Help Desk Ticket'
        verbose_name_plural = 'Help Desk Tickets'

"""

class TestModelWritingBot(TestCase):
    def setUp(self):
        super().setUp()
        self.user_input = 'Add name to the help desk ticket model. Description should be null true'
        self.model_file = model_file_data

    def test_model_orchestration_bot(self):
        # Pulls apart the users request and decides which bots to call to make changes to the model field.
        # Entry point for CLI
        model_file = bots.ModelOrchestrationBot().process(user_input=self.user_input)
        self.assertIsNotNone(model_file)

    def test_model_field_identifier_bot(self):
        # Identifies the fields that need to be changed and enriches the data.
        fields = bots.ModelFieldIdentifierBot().process(user_input=self.user_input, model_file=self.model_file)
        print(fields)
        self.assertIsNotNone(fields)

    def test_model_field_orchestration_bot(self):
        # Identifies the fields that need to be changed and enriches the data.
        model_file = bots.ModelFieldOrchestrationBot().process(user_input=self.user_input, model_file=self.model_file)
        print(model_file)
        self.assertIsNotNone(model_file)

    def test_model_writing_bot(self):
        # Next step is to actually write the fields.
        model_intel = bots.ModelFieldGeneralProgrammerBot().process(user_input=self.user_input)
        self.assertIsNotNone(model_intel)

    def test_model_review_bot(self):
        # Need to review the model file as a whole to ensure it follows best practices.
        model_intel = bots.ModelFieldGeneralProgrammerBot().process(user_input=self.user_input)
        self.assertIsNotNone(model_intel)

    def test_model_file_finding_bot(self):
        # Find the file correctly. Needs to be improved and made repeatable.
        model_file = bots.ModelFileFinderBot().process(user_input=self.user_input)
        self.assertIsNotNone(model_file)
