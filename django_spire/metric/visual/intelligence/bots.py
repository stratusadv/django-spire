from __future__ import annotations

from dandy import Bot

from django_spire.metric.visual.intelligence import intel, prompts


class VisualBot(Bot):
    llm_intel_class = intel.VisualIntel
    llm_role = prompts.visual_instruction_prompt()

    def process(
        self,
        user_input: str
    ) -> intel.VisualIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.visual_user_input_prompt(user_input)
        )
