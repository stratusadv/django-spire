from dandy.llm import BaseLlmBot, LlmConfigOptions


from django_spire.contrib.seeding.intelligence.intel import SourceIntel


from django_spire.contrib.seeding.intelligence.prompts.generate_django_model_seeder_prompts import \
    generate_django_model_seeder_user_prompt, generate_django_model_seeder_system_prompt


class SeederGeneratorBot(BaseLlmBot):

    config = 'DEEP_SEEK'

    config_options = LlmConfigOptions(
        temperature=0.3,
        randomize_seed=True
    )

    @classmethod
    def process(
            cls,
            model_import: str,
            model_description: str
    ):
        return cls.process_prompt_to_intel(
            prompt=generate_django_model_seeder_user_prompt(
                model_import,
                model_description,
            ),
            intel_class=SourceIntel,
            postfix_system_prompt=generate_django_model_seeder_system_prompt()
        )
