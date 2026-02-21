from __future__ import annotations

from django.test import TestCase

from django_spire.contrib.programmer.models import bots

class TestModelWritingBot(TestCase):

    def test_model_orchestration_bot(self):
        model_file = bots.ModelOrchestrationBot().process(
            user_input='Add name to the help desk ticket model. Description should be null true'
        )
        print(model_file)
        self.assertIsNotNone(model_file)

    def test_model_writing_bot(self):
        model_intel = bots.ModelProgrammerBot().process(
            user_input='Add name to the help desk ticket model.',
        )

        self.assertIsNotNone(model_intel)

    def test_model_file_finding_bot(self):
        file_path_intel = bots.ModelFileFinderBot().process(
            user_input='I want to add the following fields to my help desk model',
        )

        self.assertIsNotNone(file_path_intel)
