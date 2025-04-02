from dandy.llm import Prompt


def generate_django_model_seeder_system_prompt() -> Prompt:
    return (
        Prompt()
        .title('Your a coder that needs to write a DjangoModelSeeder based on the users input.')
        .divider()
        .text(
            'Follow the rules below and the provided code to create a DjangoModelSeeder based on the users input')
        .list([
            'Make the seeder work as per the documenation',
        ])
        .line_break()
        .module_source('django_spire.seeding.model.base')
    )


def generate_django_model_seeder_user_prompt(
        model_import: str,
        model_description: str
) -> Prompt:
    return (
        Prompt()
        .heading('Django Model Description')
        .text(model_description)
        .line_break()
        .module_source(model_import)
    )
