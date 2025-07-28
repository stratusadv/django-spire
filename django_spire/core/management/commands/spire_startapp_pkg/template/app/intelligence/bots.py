from dandy.llm import BaseLlmBot

from module.intelligence import prompts
from module.intelligence import intel


class SpireChildAppBot(BaseLlmBot):
    instructions_prompt = prompts.spirechildapp_instruction_prompt()
    intel_class = intel.SpireChildAppIntel

    @classmethod
    def process(
            cls,
            user_input: str
    ) -> intel.SpireChildAppIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.spirechildapp_user_input_prompt(user_input)
        )
