from __future__ import annotations

from dandy import Bot

from django_spire.metric.visual.presentation.intelligence import intel, prompts


class PresentationBot(Bot):
    llm_intel_class = intel.PresentationIntel
    llm_role = prompts.presentation_instruction_prompt()

    def process(
        self,
        user_input: str
    ) -> intel.PresentationIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.presentation_user_input_prompt(user_input)
        )
