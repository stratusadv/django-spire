from __future__ import annotations

from dandy import Bot, Prompt

from django_spire.ai.prompt.tuning import prompts, intel


class PromptTestingBot(Bot):
    role = Prompt()

    def process(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> intel.PromptTestingIntel:
        self.role = system_prompt
        self.llm.options.temperature = 0.5

        return self.llm.prompt_to_intel(
            prompt=user_prompt,
            intel_class=intel.PromptTestingIntel
        )


class SimplePromptTuningBot(Bot):
    role = prompts.prompt_tuning_instruction_bot_prompt()

    def process(
        self,
        prompt: str,
        feedback: str
    ) -> intel.PromptTuningIntel:
        self.llm.options.temperature = 0.2
        return self.llm.prompt_to_intel(
            prompt=prompts.prompt_tuning_input_prompt(prompt, feedback),
            intel_class=intel.PromptTuningIntel
        )


class AdvancedPromptTuningBot(Bot):
    role = prompts.prompt_tuning_instruction_bot_prompt()

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
    role = prompts.formatting_bot_instruction_prompt()

    def process(self, system_prompt: str) -> intel.PromptTuningIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            intel_class=intel.PromptTuningIntel
        )


class InstructionClarityBot(Bot):
    role = prompts.instruction_clarity_bot_instruction_prompt()

    def process(self, system_prompt: str) -> intel.PromptTuningIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            intel_class=intel.PromptTuningIntel
        )


class PersonaBot(Bot):
    role = prompts.persona_bot_instruction_prompt()

    def process(self, system_prompt: str) -> intel.PromptTuningIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            intel_class=intel.PromptTuningIntel
        )


class DuplicationRemovalBot(Bot):
    role = prompts.duplication_removal_bot_instruction_prompt()

    def process(self, system_prompt: str) -> intel.PromptTuningIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            intel_class=intel.PromptTuningIntel
        )


class ExampleOptimizationBot(Bot):
    role = prompts.example_optimization_bot_instruction_prompt()

    def process(self, system_prompt: str) -> intel.PromptTuningIntel:
        return self.llm.prompt_to_intel(
            prompt=prompts.specialized_bot_input_prompt(system_prompt),
            intel_class=intel.PromptTuningIntel
        )
