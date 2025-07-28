from dandy.llm import BaseLlmBot

from django_spire.ai.prompt.tuning import prompts, intel


class PromptTuningBot(BaseLlmBot):
    instructions_prompt = prompts.prompt_tuning_instruction_bot_prompt()
    intel_class = intel.PromptTuningIntel

    @classmethod
    def process(
            cls,
            system_prompt: str,
            feedback: str,

    ) -> intel.PromptTuningIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.prompt_tuning_input_prompt(system_prompt, feedback),
            postfix_system_prompt=None
        )



