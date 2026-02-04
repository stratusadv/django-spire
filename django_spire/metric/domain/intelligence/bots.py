from __future__ import annotations

from dandy import Bot

from django_spire.metric.domain.intelligence import intel, prompts


class DomainBot(Bot):
    llm_intel_class = intel.DomainIntel
    llm_role = prompts.domain_instruction_prompt()

    def process(
        self,
        user_input: str
    ) -> intel.DomainIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.domain_user_input_prompt(user_input)
        )
