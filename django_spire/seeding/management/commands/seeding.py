from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from dandy.llm import LlmBot
from dandy.conf import settings

from django_spire.seeding.intelligence.intel import SourceIntel
from django_spire.seeding.intelligence.prompts.generate_django_model_seeder_prompts import \
    generate_django_model_seeder_user_prompt, generate_django_model_seeder_system_prompt


_SEEDING_OUTPUT_PATH = Path(settings.BASE_PATH, '.seeding_generator_output')


class Command(BaseCommand):
    help = 'Generate a Seeder'

    def add_arguments(self, parser):
        parser.add_argument(
            'model_import',
            type=str,
            help='The import path to the Django model class',
        )

        parser.add_argument(
            'model_description',
            type=str,
            help='A small descript of the model',
            nargs='+',
        )

    def handle(self, *args, **kwargs):
        if not kwargs['model_import'] or not kwargs['model_description']:
            raise CommandError('You must provide a model import path and a model description')

        model_import = kwargs['model_import']
        model_description = ' '.join(kwargs['model_description'])

        source_intel = LlmBot.process(
            prompt=generate_django_model_seeder_user_prompt(
                model_import,
                model_description,
            ),
            intel_class=SourceIntel,
            postfix_system_prompt=generate_django_model_seeder_system_prompt()
        )

        Path(_SEEDING_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

        with open(Path(_SEEDING_OUTPUT_PATH, source_intel.file_name), 'w') as f:
            f.write(source_intel.source)

        self.stdout.write(f'Done ... saved to "{Path(_SEEDING_OUTPUT_PATH, source_intel.file_name)}"')
