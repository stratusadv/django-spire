from __future__ import annotations

from dandy import Bot

from django_spire.metric.domain.statistic.intelligence import intel, prompts


class StatisticBot(Bot):
    llm_intel_class = intel.StatisticIntel
    llm_role = prompts.statistic_instruction_prompt()

    def process(
        self,
        user_input: str
    ) -> intel.StatisticIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.statistic_user_input_prompt(user_input)
        )
