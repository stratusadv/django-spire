from __future__ import annotations

from dandy import Bot

from test_project.apps.lazy_tabs.intelligence import intel, prompts


class LazyTabsBot(Bot):
    intel_class = intel.LazyTabsIntel
    role = prompts.lazy_tabs_instruction_prompt()

    def process(
        self,
        user_input: str
    ) -> intel.LazyTabsIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.lazy_tabs_user_input_prompt(user_input)
        )
