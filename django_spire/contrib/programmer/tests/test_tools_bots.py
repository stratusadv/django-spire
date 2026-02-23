from __future__ import annotations

from django.test import TestCase

from django_spire.contrib.programmer.models.bots.general_bots import ModelFinderBot
from django_spire.contrib.programmer.models.bots.model_bots import ModelFieldGeneralProgrammerBot, \
    ModelFieldOrchestrationBot, ModelFieldIdentifierBot
from django_spire.contrib.programmer.models.bots.orchestration_bots import ModelOrchestrationBot
from django_spire.contrib.programmer.models.bots.user_input_bots import ModelEnrichmentPrompt
from django_spire.contrib.programmer.tools.bots import ManagerBot, ProjectChampion, project_execution_workflow


class TestToolBot(TestCase):

    def test_project_execution_workflow(self):
        project_execution_workflow('Tell me a funny joke.')

    def test_project_champion(self):
        champion = ProjectChampion().process(prompt='I want to know a funny joke.')

    def test_manager_bot(self):
        manager = ManagerBot().process('')
