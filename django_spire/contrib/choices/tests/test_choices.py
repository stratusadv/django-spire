import json

from django_spire.contrib.choices.choices import SpireTextChoices
from django_spire.core.tests.test_cases import BaseTestCase


class TestSpireTextChoices(BaseTestCase):
    def setUp(self):
        class StatusChoices(SpireTextChoices):
            DRAFT = ('dra', 'Draft')
            PUBLISHED = ('pub', 'Published')
            ARCHIVED = ('arc', 'Archived')


        self.StatusChoices = StatusChoices

    def test_inherits_from_text_choices(self):
        assert issubclass(self.StatusChoices, SpireTextChoices), self.StatusChoices.__class__

    def test_choices_property_exists(self):
        assert hasattr(self.StatusChoices, 'choices'), self.StatusChoices.dir()
        assert self.StatusChoices.choices is not None, self.StatusChoices.choices

    def test_to_glue_choices_returns_string(self):
        result = self.StatusChoices.to_glue_choices()
        assert isinstance(result, str), type(result)

    def test_to_glue_choices_returns_valid_json(self):
        result = self.StatusChoices.to_glue_choices()
        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
            assert 'to_glue_choices did not return valid JSON'

    def test_to_glue_choices_correct_structure(self):
        result = self.StatusChoices.to_glue_choices()
        parsed = json.loads(result)

        assert isinstance(parsed, list), type(parsed)
        assert len(parsed) == 3

        assert parsed[0] == ['dra', 'Draft']
        assert parsed[1] == ['pub', 'Published']
        assert parsed[2] == ['arc', 'Archived']

    def test_empty_choices(self):
        class EmptyChoices(SpireTextChoices):
            pass


        result = EmptyChoices.to_glue_choices()
        parsed = json.loads(result)
        assert parsed == []

    def test_single_choice(self):
        class SingleChoice(SpireTextChoices):
            ONLY = 'only', 'Only Option'


        result = SingleChoice.to_glue_choices()
        parsed = json.loads(result)
        assert parsed == [['only', 'Only Option']]
