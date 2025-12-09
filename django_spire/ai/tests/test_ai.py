from __future__ import annotations

from dandy import BaseIntel, Bot, recorder_to_html_file

from django_spire.ai.decorators import log_ai_interaction_from_recorder
from django_spire.ai.models import AiInteraction, AiUsage
from django_spire.core.tests.test_cases import BaseTestCase


class HorseIntel(BaseIntel):
    breed: str
    color: str
    first_name: str
    has_cone_taped_to_head: bool


class AiDecoratorTestCase(BaseTestCase):
    def test_ai_interaction_decorator_creates_usage_record(self) -> None:
        initial_count = AiUsage.objects.count()

        @log_ai_interaction_from_recorder(self.super_user, 'horse')
        @recorder_to_html_file('horse')
        def generate_horse_intel(user_input: str) -> HorseIntel:
            bot = Bot()
            return bot.llm.prompt_to_intel(
                prompt=user_input,
                intel_class=HorseIntel,
            )

        horse_intel = generate_horse_intel('Make me a magical horse that grants wishes!')

        assert horse_intel.first_name != ''
        assert AiUsage.objects.count() >= initial_count

    def test_ai_interaction_decorator_creates_interaction_record(self) -> None:
        initial_count = AiInteraction.objects.count()

        @log_ai_interaction_from_recorder(self.super_user, 'test_actor')
        @recorder_to_html_file('test_interaction')
        def generate_horse_intel(user_input: str) -> HorseIntel:
            bot = Bot()
            return bot.llm.prompt_to_intel(
                prompt=user_input,
                intel_class=HorseIntel,
            )

        generate_horse_intel('Create a horse')

        assert AiInteraction.objects.count() > initial_count

    def test_ai_interaction_decorator_requires_user_or_actor(self) -> None:
        try:
            @log_ai_interaction_from_recorder()
            def dummy_func() -> None:
                pass
        except ValueError as e:
            assert 'user or actor must be provided' in str(e)
        else:
            assert False, 'Expected ValueError'

    def test_ai_interaction_decorator_with_actor_only(self) -> None:
        @log_ai_interaction_from_recorder(actor='test_actor_only')
        @recorder_to_html_file('test_actor_only')
        def generate_horse_intel(user_input: str) -> HorseIntel:
            bot = Bot()
            return bot.llm.prompt_to_intel(
                prompt=user_input,
                intel_class=HorseIntel,
            )

        horse_intel = generate_horse_intel('Create a horse')

        assert horse_intel is not None

        interaction = AiInteraction.objects.filter(actor='test_actor_only').first()
        assert interaction is not None
        assert interaction.actor == 'test_actor_only'

    def test_ai_interaction_decorator_records_module_and_callable(self) -> None:
        @log_ai_interaction_from_recorder(self.super_user, 'module_test')
        @recorder_to_html_file('module_test')
        def test_callable(user_input: str) -> HorseIntel:
            bot = Bot()
            return bot.llm.prompt_to_intel(
                prompt=user_input,
                intel_class=HorseIntel,
            )

        test_callable('Test input')

        interaction = AiInteraction.objects.filter(actor='module_test').first()
        assert interaction is not None
        assert 'test_callable' in interaction.callable_name


class AiUsageModelTestCase(BaseTestCase):
    def test_ai_usage_str(self) -> None:
        ai_usage = AiUsage.objects.create()

        assert 'ai usage' in str(ai_usage)

    def test_ai_usage_default_values(self) -> None:
        ai_usage = AiUsage.objects.create()

        assert ai_usage.event_count == 0
        assert ai_usage.token_usage == 0
        assert ai_usage.run_time_seconds == 0.0
        assert ai_usage.was_successful is True


class AiInteractionModelTestCase(BaseTestCase):
    def test_ai_interaction_str(self) -> None:
        ai_usage = AiUsage.objects.create()
        ai_interaction = AiInteraction.objects.create(
            ai_usage=ai_usage,
            actor='test_actor',
            module_name='test_module',
            callable_name='test_callable',
        )

        assert 'test_actor' in str(ai_interaction)
        assert 'interaction' in str(ai_interaction)

    def test_ai_interaction_saves_user_info(self) -> None:
        ai_usage = AiUsage.objects.create()
        ai_interaction = AiInteraction.objects.create(
            ai_usage=ai_usage,
            user=self.super_user,
            actor=None,
            module_name='test_module',
            callable_name='test_callable',
        )

        assert ai_interaction.user_email == self.super_user.email
        assert ai_interaction.user_first_name == self.super_user.first_name
        assert ai_interaction.user_last_name == self.super_user.last_name

    def test_ai_interaction_default_values(self) -> None:
        ai_usage = AiUsage.objects.create()
        ai_interaction = AiInteraction.objects.create(
            ai_usage=ai_usage,
            actor='test',
            module_name='test',
            callable_name='test',
        )

        assert ai_interaction.event_count == 0
        assert ai_interaction.token_usage == 0
        assert ai_interaction.run_time_seconds == 0.0
        assert ai_interaction.was_successful is True
        assert ai_interaction.exception is None
        assert ai_interaction.stack_trace is None
