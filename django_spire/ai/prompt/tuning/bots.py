from __future__ import annotations

from dandy import Bot, LlmConfigOptions, Prompt

from django_spire.ai.prompt.tuning import prompts, intel


class PromptTestingBot(Bot):
    llm_role = Prompt()
    llm_config_options = LlmConfigOptions(temperature=0.4)

    def process(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> intel.PromptTestingIntel:
        self.llm_role = system_prompt
        return self.llm.prompt_to_intel(
            prompt=user_prompt,
            intel_class=intel.PromptTestingIntel
        )


class SimplePromptTuningBot(Bot):
    llm_role = prompts.prompt_tuning_instruction_bot_prompt()
    llm_config_options = LlmConfigOptions(temperature=0.1)

    def process(
        self,
        prompt: str,
        feedback: str
    ) -> intel.PromptTuningIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.prompt_tuning_input_prompt(prompt, feedback),
            intel_class=intel.PromptTuningIntel
        )


class AdvancedPromptTuningBot(Bot):
    llm_role = prompts.prompt_tuning_instruction_bot_prompt()

    def process(
        self,
        system_prompt: str,
        feedback: str
    ) -> intel.PromptTuningIntel:
        simple_bot = SimplePromptTuningBot()
        formatting_bot = FormattingBot()
        duplication_bot = DuplicationRemovalBot()
        instruction_bot = InstructionClarityBot()
        example_bot = ExampleOptimizationBot()
        persona_bot = PersonaBot()

        tuned_prompt = simple_bot.process(system_prompt, feedback)
        formatted_prompt = formatting_bot.process(tuned_prompt.prompt)
        remove_duplicates = duplication_bot.process(formatted_prompt.prompt)
        improve_instructions = instruction_bot.process(remove_duplicates.prompt)
        example_optimization = example_bot.process(improve_instructions.prompt)
        return persona_bot.process(example_optimization.prompt)


class FormattingBot(Bot):
    llm_role = prompts.formatting_bot_instruction_prompt()

    def process(self, system_prompt: str) -> intel.PromptTuningIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            intel_class=intel.PromptTuningIntel,
            postfix_system_prompt=None
        )


class InstructionClarityBot(Bot):
    llm_role = prompts.instruction_clarity_bot_instruction_prompt()

    def process(self, system_prompt: str) -> intel.PromptTuningIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            intel_class=intel.PromptTuningIntel,
            postfix_system_prompt=None
        )


class PersonaBot(Bot):
    llm_role = prompts.persona_bot_instruction_prompt()

    def process(self, system_prompt: str) -> intel.PromptTuningIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            intel_class=intel.PromptTuningIntel,
            postfix_system_prompt=None
        )


class DuplicationRemovalBot(Bot):
    llm_role = prompts.duplication_removal_bot_instruction_prompt()

    def process(self, system_prompt: str) -> intel.PromptTuningIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            intel_class=intel.PromptTuningIntel,
            postfix_system_prompt=None
        )


class ExampleOptimizationBot(Bot):
    llm_role = prompts.example_optimization_bot_instruction_prompt()

    def process(self, system_prompt: str) -> intel.PromptTuningIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            intel_class=intel.PromptTuningIntel,
            postfix_system_prompt=None
        )
