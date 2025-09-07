from dandy.llm import BaseLlmBot

from test_project.apps.ordering.intelligence import prompts
from test_project.apps.ordering.intelligence import intel


class OrderingBot(BaseLlmBot):
    instructions_prompt = prompts.ordering_instruction_prompt()
    intel_class = intel.OrderingIntel

    @classmethod
    def process(
            cls,
            user_input: str
    ) -> intel.OrderingIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.ordering_user_input_prompt(user_input)
        )
