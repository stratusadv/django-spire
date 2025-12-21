from __future__ import annotations

from django_spire.ai.prompt.tuning.prompts import (
    duplication_removal_bot_instruction_prompt,
    example_optimization_bot_instruction_prompt,
    formatting_bot_instruction_prompt,
    instruction_clarity_bot_instruction_prompt,
    persona_bot_instruction_prompt,
    prompt_tuning_input_prompt,
    prompt_tuning_instruction_bot_prompt,
    specialized_bot_input_prompt,
)
from django_spire.ai.prompt.tuning.choices import OutcomeRatingChoices
from django_spire.ai.prompt.tuning.intel import PromptTestingIntel, PromptTuningIntel
from django_spire.core.tests.test_cases import BaseTestCase


class OutcomeRatingChoicesTests(BaseTestCase):
    def test_terrible_rating(self) -> None:
        assert OutcomeRatingChoices.TERRIBLE.value == 1
        assert OutcomeRatingChoices.TERRIBLE.label == 'terrible'

    def test_bad_rating(self) -> None:
        assert OutcomeRatingChoices.BAD.value == 2
        assert OutcomeRatingChoices.BAD.label == 'bad'

    def test_ok_rating(self) -> None:
        assert OutcomeRatingChoices.OK.value == 3
        assert OutcomeRatingChoices.OK.label == 'ok'

    def test_good_rating(self) -> None:
        assert OutcomeRatingChoices.GOOD.value == 4
        assert OutcomeRatingChoices.GOOD.label == 'good'

    def test_great_rating(self) -> None:
        assert OutcomeRatingChoices.GREAT.value == 5
        assert OutcomeRatingChoices.GREAT.label == 'great'

    def test_amazing_rating(self) -> None:
        assert OutcomeRatingChoices.AMAZING.value == 6
        assert OutcomeRatingChoices.AMAZING.label == 'amazing'

    def test_all_ratings_count(self) -> None:
        assert len(OutcomeRatingChoices) == 6


class PromptTuningIntelTests(BaseTestCase):
    def test_prompt_tuning_intel_creation(self) -> None:
        intel = PromptTuningIntel(prompt='Test prompt')

        assert intel.prompt == 'Test prompt'

    def test_prompt_tuning_intel_empty_prompt(self) -> None:
        intel = PromptTuningIntel(prompt='')

        assert intel.prompt == ''

    def test_prompt_tuning_intel_long_prompt(self) -> None:
        long_prompt = 'A' * 10000
        intel = PromptTuningIntel(prompt=long_prompt)

        assert intel.prompt == long_prompt
        assert len(intel.prompt) == 10000


class PromptTestingIntelTests(BaseTestCase):
    def test_prompt_testing_intel_creation(self) -> None:
        intel = PromptTestingIntel(result='Test result')

        assert intel.result == 'Test result'

    def test_prompt_testing_intel_empty_result(self) -> None:
        intel = PromptTestingIntel(result='')

        assert intel.result == ''


class PromptTuningPromptsTests(BaseTestCase):
    def test_prompt_tuning_instruction_bot_prompt(self) -> None:
        prompt = prompt_tuning_instruction_bot_prompt()

        assert prompt is not None
        assert 'System Prompt Tuning Expert' in prompt.to_str()

    def test_prompt_tuning_input_prompt(self) -> None:
        prompt = prompt_tuning_input_prompt('Test system prompt', 'Test feedback')

        assert prompt is not None
        assert 'Test system prompt' in prompt.to_str()
        assert 'Test feedback' in prompt.to_str()

    def test_formatting_bot_instruction_prompt(self) -> None:
        prompt = formatting_bot_instruction_prompt()

        assert prompt is not None
        assert 'Prompt Formatting Expert' in prompt.to_str()

    def test_instruction_clarity_bot_instruction_prompt(self) -> None:
        prompt = instruction_clarity_bot_instruction_prompt()

        assert prompt is not None
        assert 'Instruction Clarity Expert' in prompt.to_str()

    def test_persona_bot_instruction_prompt(self) -> None:
        prompt = persona_bot_instruction_prompt()

        assert prompt is not None
        assert 'Persona Consistency Expert' in prompt.to_str()

    def test_duplication_removal_bot_instruction_prompt(self) -> None:
        prompt = duplication_removal_bot_instruction_prompt()

        assert prompt is not None
        assert 'Duplication Removal Expert' in prompt.to_str()

    def test_example_optimization_bot_instruction_prompt(self) -> None:
        prompt = example_optimization_bot_instruction_prompt()

        assert prompt is not None
        assert 'Example Optimization Expert' in prompt.to_str()

    def test_specialized_bot_input_prompt(self) -> None:
        prompt = specialized_bot_input_prompt('Test system prompt')

        assert prompt is not None
        assert 'Test system prompt' in prompt.to_str()
