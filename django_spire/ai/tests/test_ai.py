from __future__ import annotations

from dandy import BaseIntel, Bot, recorder_to_html_file

from django_spire.ai.decorators import log_ai_interaction_from_recorder
from django_spire.core.tests.test_cases import BaseTestCase


class AiTestCase(BaseTestCase):
    def test_ai_interaction_decorator(self):
        class HorseIntel(BaseIntel):
            first_name: str
            breed: str
            color: str
            has_cone_taped_to_head: bool

        @log_ai_interaction_from_recorder(self.super_user, 'horse')
        @recorder_to_html_file('horse')
        def generate_horse_intel(user_input: str) -> HorseIntel:
            bot = Bot()
            return bot.llm.prompt_to_intel(
                prompt=user_input,
                intel_class=HorseIntel,
            )

        horse_intel = generate_horse_intel('Make me a magical horse that grants wishes!')

        self.assertNotEqual(horse_intel.first_name, '')
