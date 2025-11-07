from dandy import Bot, LlmConfigOptions

from django_spire.contrib.seeding.intelligence.intel import SourceIntel
from django_spire.contrib.seeding.intelligence.prompts.generate_django_model_seeder_prompts import (
    generate_django_model_seeder_user_prompt,
    generate_django_model_seeder_system_prompt
)


class SeederGeneratorBot(Bot):
    llm_config = 'PYTHON_MODULE'

    llm_config_options = LlmConfigOptions(
        temperature=0.3,
        randomize_seed=True
    )

    llm_guidelines = generate_django_model_seeder_system_prompt()

    llm_role = 'You are an expert Python developer specializing in Django model seeders.'

    def process(
        self,
        model_import: str,
        model_description: str
    ) -> SourceIntel:
        return self.llm.prompt_to_intel(
            prompt=generate_django_model_seeder_user_prompt(
                model_import,
                model_description,
            ),
            intel_class=SourceIntel
        )
