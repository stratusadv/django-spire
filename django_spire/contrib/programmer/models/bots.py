from pathlib import Path

from dandy import Bot, Prompt
from dandy.file.utils import get_directory_listing

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

    def process(self, user_input: str, model_file: str) -> intel.PythonFileIntel:
        # action_bots = self.llm.decoder.prompt_to_values(
        #     prompt=prompt,
        #     keys_description='Actions a programmer takes on a django models.py file.',
        #     keys_values={
        #         'Adding or updating model fields': 'fie',
        #         'writing or editing model methods': 'met',
        #     }
        # )
        #
        # for action_bot in action_bots.values:
        #     action_bot().process(prompt=prompt)

        models_prompt = (
            Prompt()
            .heading('Make the following changes to the models.py file.')
            .text(user_input)
            .heading('Djagno Model File')
            .text(model_file)
        )

        return self.llm.prompt_to_intel(models_prompt)


class ModelFieldProgrammerBot(Bot):
    pass


class ModelOrchestrationBot(Bot):
    role = 'An expert at finding and orchestrating tasks that need to be completed.'
    task = 'Return actions in the correct order they need to be taken.'

    def process(self, user_input: str):
        file_path_intel = ModelFileFinderBot().process(user_input=user_input)
        model_file_path = file_path_intel.file_path

        if self.file.exists(model_file_path):
            model_file = self.file.read(model_file_path)
        else:
            model_file = ''

        actions = {
            'Add New Model Fields': 'Add New Model Fields',
            'Edit Existing Model Fields': 'Edit Existing Model Fields',
            'Add Methods to the Model': 'Add Methods to the Model',
            'Edit Methods that are already on the model': 'Edit Methods that are already on the model',
            'Create a new model file': 'Create a new model file',
            'Review a model file based on our best practices': 'Review a model file based on our best practices',
            'Configure default ordering': 'Configure default ordering',
            'Set the verbose names': 'Set the verbose names',
            'Set the database table path': 'Set the database table path',
            'Configure Breadcrumbs': 'Configure Breadcrumbs',
        }

        prompt = (
            Prompt()
            .heading('User Request')
            .text(user_input)
            .heading('Typical Order of Events')
            .ordered_list([
                'Create the model file if it is empty',
                'Configure meta fields if new file.',
                'Write or edit fields',
                'Write or edit methods',
                'Review for best practices'
            ])
            .heading('Model File')
            .text(model_file)
        )

        action_bots = self.llm.decoder.prompt_to_values(
            prompt=prompt,
            keys_description='Actions a programmer takes on a django model file',
            keys_values=actions,
        )

        print(action_bots)

        # model_file = model_file
        # for bot in action_bots:
        #     model_file = bot.process(user_input=user_input, model_file=model_file)
        #
        return model_file