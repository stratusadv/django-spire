from pathlib import Path

from click import prompt
from dandy import Bot, Prompt
from dandy.file.utils import get_directory_listing
from dandy.intel.intel import DefaultIntel

from django_spire.contrib.programmer.models import intel

_RELATIVE_BASE_DIR = Path(Path(__file__).parent).resolve()
BEST_PRACTICES = Path(_RELATIVE_BASE_DIR, 'best_practices.md')


class ModelFileFinderBot(Bot):
    role = 'Expert at searching file architectures to return the correct file.'
    task = 'Return the path to the located model file.'
    guidelines = (
        Prompt()
        .list([
            'Each django app has a models.py file.',
            'Our software architecture uses a nested hierarchy.'
        ])
    )
    intel_class = intel.FilePathIntel

    def process(self, user_input: str) -> intel.FilePathIntel:
        # Find the correct model file...
        # This return a lot of directories... need to crawl it to get better results?

        class ModelNameFormatterBot(Bot):
            role = 'Expert in finding django model names in text.'
            task = 'Return a string of a django model name.'
            guidelines = 'Simply the users request and return the app name and model name of a django model.'

        model_name = ModelNameFormatterBot().process(user_input)
        directories = (get_directory_listing(_RELATIVE_BASE_DIR.parent.parent.parent.resolve()))

        prompt = (
            Prompt()
            .heading('Model to Find')
            .text(model_name.text)
            .heading('Directories to Choose From')
            .list(directories)
        )

        return self.llm.prompt_to_intel(prompt)


class ModelProgrammerBot(Bot):
    role = 'World class python & django developer who focuses on simplicity.'
    task = 'Return a django model python file based on the best practices provided.'
    guidelines = (
        Prompt()
        .heading('Best Practices')
        .file(BEST_PRACTICES)
    )
    intel_class = intel.PythonFileIntel

    def process(self, prompt: str, model_file: str) -> intel.PythonFileIntel:
        # This should always have a model file passed to it...

        # check to see if the model file exists or we need to create one.

        # create a new model file structure using our best practices.

        model_intel = self.llm.prompt_to_intel(prompt)

        action_bots = self.llm.decoder.prompt_to_values(
            prompt=prompt,
            keys_description='Actions a programmer takes on a django models.py file.',
            keys_values={
                'Adding or updating model fields': 'fie',
                'writing or editing model methods': 'met',
            }
        )

        for action_bot in action_bots.values:
            action_bot().process(prompt=prompt)

        return self.llm.prompt_to_intel(prompt)


class ModelFieldProgrammerBot(Bot):
    pass