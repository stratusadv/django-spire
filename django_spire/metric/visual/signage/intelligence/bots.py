from __future__ import annotations

from dandy import Bot

from django_spire.metric.visual.signage.intelligence import intel, prompts


class SignageBot(Bot):
    llm_intel_class = intel.SignageIntel
    llm_role = prompts.signage_instruction_prompt()

    def process(
        self,
        user_input: str
    ) -> intel.SignageIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.signage_user_input_prompt(user_input)
        )
