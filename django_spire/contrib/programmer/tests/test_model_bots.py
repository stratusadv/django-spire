from __future__ import annotations

from django.test import TestCase

from django_spire.contrib.programmer.models.bots.general_bots import ModelFinderBot
from django_spire.contrib.programmer.models.bots.model_bots import ModelFieldGeneralProgrammerBot, \
    ModelFieldOrchestrationBot, ModelFieldIdentifierBot
from django_spire.contrib.programmer.models.bots.orchestration_bots import ModelOrchestrationBot
from django_spire.contrib.programmer.models.bots.user_input_bots import ModelEnrichmentPrompt

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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_input = 'Add name to the help desk ticket model. Description field should be null true'
        cls.model_file = model_file_data
        cls.models_intel = ModelEnrichmentPrompt().process(prompt=cls.user_input)
        cls.model_intel = cls.models_intel.models[0]
        cls.model_name = cls.model_intel.name
        cls.enriched_user_input = cls.model_intel.to_prompt()

    def test_model_user_enrichment_bot(self):
        # prompt should produce 1 model with 2 actions
        models_intel = ModelEnrichmentPrompt().process(prompt=self.user_input)
        self.assertEqual(len(models_intel.models), 1)
        model_intel = models_intel.models[0]
        self.assertEqual(len(model_intel.actions), 2)

    # Todo: Not sure how to test dandy CLI interactions
    # def test_model_orchestration_bot(self):
    #     model_files = ModelOrchestrationBot().process(user_input=self.user_input)
    #     self.assertIsNotNone(model_files)

    def test_model_field_identifier_bot(self):
        # Identifies the fields that need to be changed and enriches the data.
        fields = ModelFieldIdentifierBot().process(user_input=self.enriched_user_input, model_file=self.model_file)
        print(fields)
        self.assertIsNotNone(fields)

    def test_model_field_orchestration_bot(self):
        # Identifies the fields that need to be changed and enriches the data.
        model_file = ModelFieldOrchestrationBot().process(user_input=self.enriched_user_input, model_file=self.model_file)
        print(model_file)
        self.assertIsNotNone(model_file)

    def test_model_writing_bot(self):
        model_file = ModelFieldGeneralProgrammerBot().process(
            prompt=self.models_intel.to_prompt(),
            model_file=model_file_data
        )
        self.assertIsNotNone(model_file)

    def test_model_review_bot(self):
        # Need to review the model file as a whole to ensure it follows best practices.
        model_intel = ModelFieldGeneralProgrammerBot().process(prompt=self.user_input)
        self.assertIsNotNone(model_intel)

    def test_model_file_finding_bot(self):
        # Find the file correctly. Needs to be improved and made repeatable.
        model_file = ModelFinderBot().process(model_name=self.model_name)
        self.assertIn('help_desk', model_file.path)
