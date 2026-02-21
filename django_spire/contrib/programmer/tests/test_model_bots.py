from __future__ import annotations

from django.test import TestCase

from django_spire.contrib.programmer.models import bots

class TestModelWritingBot(TestCase):

    def test_model_writing_bot(self):
        model_intel = bots.ModelProgrammerBot().process(
            prompt='Write a person model with a first name and last name. It needs a FK to a company. Gender choices of male and female.',
        )

        print(model_intel.python_file)
        self.assertIsNotNone(model_intel)

    def test_model_file_finding_bot(self):
        file_path_intel = bots.ModelFileFinderBot().process(
            user_input='I want to add the following fields to my help desk model',
        )
        print(file_path_intel.file_path)

        self.assertIsNotNone(file_path_intel)
