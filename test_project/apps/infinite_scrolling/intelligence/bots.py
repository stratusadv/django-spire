from __future__ import annotations

from dandy import Bot

from test_project.apps.infinite_scrolling.intelligence import intel, prompts


class InfiniteScrollingBot(Bot):
    intel_class = intel.InfiniteScrollingIntel
    role = prompts.infinite_scrolling_instruction_prompt()

    def process(
        self,
        user_input: str
    ) -> intel.InfiniteScrollingIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.infinite_scrolling_user_input_prompt(user_input)
        )
