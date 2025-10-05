from dandy import Bot

from test_project.apps.ordering.intelligence import intel, prompts


class OrderingBot(Bot):
    llm_role = prompts.ordering_instruction_prompt()
    llm_intel_class = intel.OrderingIntel

    def process(
        self,
        user_input: str
    ) -> intel.OrderingIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.ordering_user_input_prompt(user_input)
        )
