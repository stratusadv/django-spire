from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from dandy.conf import settings
from dandy.recorder import recorder_to_html_file

from django_spire.contrib.seeding.intelligence.bots.seeder_generator_bot import SeederGeneratorBot


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

    @recorder_to_html_file('seeding_generator')
    def handle(self, *args, **kwargs):
        if not kwargs['model_import'] or not kwargs['model_description']:
            raise CommandError('You must provide a model import path and a model description')

        model_import = kwargs['model_import']
        model_description = ' '.join(kwargs['model_description'])

        source_intel = SeederGeneratorBot.process(model_import, model_description)

        Path(_SEEDING_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

        with open(Path(_SEEDING_OUTPUT_PATH, source_intel.file_name), 'w') as f:
            f.write(source_intel.python_source_code)

        self.stdout.write(f'Done ... saved to "{Path(_SEEDING_OUTPUT_PATH, source_intel.file_name)}"')
