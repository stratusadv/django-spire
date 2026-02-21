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

    def process(self, user_input: str) -> str:
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
        file_path_intel = self.llm.prompt_to_intel(prompt)

        model_file_path = file_path_intel.file_path

        if self.file.exists(model_file_path):
            model_file = self.file.read(model_file_path)
        else:
            model_file = ''

        return model_file


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


class ModelFieldIdentifierBot(Bot):
    role = 'Expert at python, django and data structures.'
    task = 'Identify each model field and enrich the data.'
    guidelines = (
        Prompt()
        .list([            
            'Be diligent. The user can be asking about many fields or a single field. We do not want to miss any field changes.',
            'Field type specific django model fields (eg. character field, text field).',
            'Description is how the field relates to the model. Give context to make better technical decisions.',
            'Technical requirements are the arguments that go into the field.',
            'Focus on the user requests and use the model field for context to make better decisions.'
        ])
    )
    intel_class = intel.ModelFieldsIntel
    
    def process(self, user_input: str, model_file: str):
        prompt = (
            Prompt()
            .heading('User Request')
            .text(user_input)
            .heading('Djagno Model File')
            .text(model_file)
        )
        return self.llm.prompt_to_intel(prompt)


class ModelFieldOrchestrationBot(Bot):
    role = 'An expert at deciding on data structure types.'
    task = 'Find the correct field for the data structure.'
    intel_class = intel

    def process(self, user_input: str, model_file: str):
        # Find all fields and enrich the data
        model_fields_intel = ModelFieldIdentifierBot().process(user_input, model_file)

        programmer_bots = {
            'Choice Field Bot': self,
            'ForeignKey Bot': self,
            'Regular Bot (used for all other choices)': self
        }

        for model_field in model_fields_intel.fields:
            # Pass enriched data to specific field programmer bots
            field_programmer_bot = self.llm.decoder.prompt_to_value(
                prompt=model_field.to_prompt(),
                keys_description='Bots to program the model field.',
                keys_values=programmer_bots
            )

            model_file = field_programmer_bot.process(user_input=model_field.to_prompt(), model_file=model_file)

        return model_file


class ModelOrchestrationBot(Bot):
    role = 'An expert at finding and orchestrating tasks that need to be completed.'
    task = 'Return actions in the correct order they need to be taken.'
    guidelines = (
        Prompt()
        .list([
            'A user will provide you with a request to perform actions on a django model.',
            'Break down that request into actions a programmer needs to take.',
            'Use the existing model file as context to help make a better decision.'
        ])
    )

    def process(self, user_input: str):
        model_file = ModelFileFinderBot().process(user_input=user_input)

        actions = {
            'Model Fields': ModelFieldOrchestrationBot,
            'Model Methods': ModelProgrammerBot,
            # 'New Model File': ModelProgrammerBot,
            # 'Review a model file': ModelProgrammerBot,
        }

        prompt = (
            Prompt()
            .heading('User Request')
            .text(user_input)
            .heading('Typical Order of Events')
            .ordered_list([
                'Create the model file if it is empty',
                'Model Fields',
                'Model Methods',
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

        for bot in action_bots:
            model_file_intel = bot().process(user_input=user_input, model_file=model_file)
            model_file = model_file_intel.python_file

        return model_file