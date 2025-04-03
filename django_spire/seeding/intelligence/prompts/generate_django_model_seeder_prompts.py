from pathlib import Path

from dandy.llm import Prompt


_RELATIVE_BASE_DIR = Path(Path(__file__).parent.parent.parent.parent.parent.resolve())


def generate_django_model_seeder_system_prompt() -> Prompt:
    return (
        Prompt()
        .title('Goal')
        .list(
            [
                'Write a DjangoModelSeeder Class for each model in the given module by the user.'
            ]
        )
        .text()
        .divider()
        .title('Return Format')
        .text('A python file that contains a DjangoModelSeeder class.')
        .text('Here is the documentation on seeding a django model.')
        # .file(Path(_RELATIVE_BASE_DIR, 'docs', 'api', 'seeding', 'overview.md'))
        # .file(Path(_RELATIVE_BASE_DIR, 'docs', 'api', 'seeding', 'getting_started.md'))
        # .file(r'C:\Users\WesleyHowery\PycharmProjects\django-spire\docs\api\seeding\overview.md')
        # .file(r'C:\Users\WesleyHowery\PycharmProjects\django-spire\docs\api\seeding\getting_started.md')
        .title('Requirements')
        .list(
            [
                'The file name should be the name of the model with a _seeder suffix.',
                'The source must be a valid Python file.',
                'Do not include triple quotes from the example.',
                'Always exclude the id field.',
            ],
        )
        .title('Specific Field Requirements.')
        .text('Follow the rules below for specific model fields.')
        .list(
            [
                "CharField with Choice Options: use faker with no method call.",
                'Foreign key: set to exclude.',
            ]
        )
        .divider()
        .title('Source Code')
        .text('Below is the source code for our seeder tools.')
        .module_source('django_spire.seeding.model.base')
        .module_source('django_spire.seeding.model.django.seeder')
        .line_break()
        .title('Example')
        .text('Below is an example of what the output should look like.')
        .module_source('django_spire.seeding.management.example')
    )


def generate_django_model_seeder_user_prompt(
        model_import: str,
        model_description: str
) -> Prompt:
    return (
        Prompt()
        .title('Django Model File')
        .module_source(model_import)
        .line_break()
        .title('Django Model Description')
        .text(model_description)
    )
