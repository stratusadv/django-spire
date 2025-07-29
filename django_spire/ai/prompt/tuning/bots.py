from dandy.llm import BaseLlmBot, LlmConfigOptions

from django_spire.ai.prompt.tuning import prompts, intel


class SimplePromptTuningBot(BaseLlmBot):
    instructions_prompt = prompts.prompt_tuning_instruction_bot_prompt()
    intel_class = intel.PromptTuningIntel
    config_options = LlmConfigOptions(temperature=0.1)


    @classmethod
    def process(
            cls,
            prompt: str,
            feedback: str,

    ) -> intel.PromptTuningIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.prompt_tuning_input_prompt(prompt, feedback),
        )


class AdvancedPromptTuningBot(BaseLlmBot):
    instructions_prompt = prompts.prompt_tuning_instruction_bot_prompt()
    intel_class = intel.PromptTuningIntel

    @classmethod
    def process(
            cls,
            system_prompt: str,
            feedback: str,

    ) -> intel.PromptTuningIntel:
        tuned_prompt = SimplePromptTuningBot.process(system_prompt, feedback)
        formatted_prompt = FormattingBot.process(tuned_prompt.prompt)
        remove_duplicates = DuplicationRemovalBot.process(formatted_prompt.prompt)
        improve_instructions = InstructionClarityBot.process(remove_duplicates.prompt)
        example_optimization = ExampleOptimizationBot.process(improve_instructions.prompt)
        persona = PersonaBot.process(example_optimization.prompt)
        return persona


        # return cls.process_prompt_to_intel(
        #     prompt=prompts.prompt_tuning_input_prompt(system_prompt, feedback),
        #     postfix_system_prompt=None
        # )
        #

class FormattingBot(BaseLlmBot):
    """Bot that preserves structure and standardizes formatting of system prompts."""
    instructions_prompt = prompts.formatting_bot_instruction_prompt()
    intel_class = intel.PromptTuningIntel

    @classmethod
    def process(
            cls,
            system_prompt: str,

    ) -> intel.PromptTuningIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            postfix_system_prompt=None
        )


class InstructionClarityBot(BaseLlmBot):
    """Bot that focuses on improving the clarity of instructions in system prompts."""
    instructions_prompt = prompts.instruction_clarity_bot_instruction_prompt()
    intel_class = intel.PromptTuningIntel

    @classmethod
    def process(
            cls,
            system_prompt: str,

    ) -> intel.PromptTuningIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            postfix_system_prompt=None
        )


class PersonaBot(BaseLlmBot):
    """Bot that maintains consistent tone and persona throughout system prompts."""
    instructions_prompt = prompts.persona_bot_instruction_prompt()
    intel_class = intel.PromptTuningIntel

    @classmethod
    def process(
            cls,
            system_prompt: str,

    ) -> intel.PromptTuningIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            postfix_system_prompt=None
        )


class DuplicationRemovalBot(BaseLlmBot):
    """Bot that identifies and removes redundancies in system prompts."""
    instructions_prompt = prompts.duplication_removal_bot_instruction_prompt()
    intel_class = intel.PromptTuningIntel

    @classmethod
    def process(
            cls,
            system_prompt: str,

    ) -> intel.PromptTuningIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            postfix_system_prompt=None
        )


class ExampleOptimizationBot(BaseLlmBot):
    """Bot that refines examples within system prompts."""
    instructions_prompt = prompts.example_optimization_bot_instruction_prompt()
    intel_class = intel.PromptTuningIntel

    @classmethod
    def process(
            cls,
            system_prompt: str,

    ) -> intel.PromptTuningIntel:

        return cls.process_prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            postfix_system_prompt=None
        )
