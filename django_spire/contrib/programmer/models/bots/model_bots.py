from __future__ import annotations

from pathlib import Path

from dandy import Bot, Prompt

from django_spire.contrib.programmer.models.intel import intel


_RELATIVE_BASE_DIR = Path(Path(__file__).parent.parent).resolve()
BEST_PRACTICES = Path(_RELATIVE_BASE_DIR, '../best_practices.md')


class ModelFieldGeneralProgrammerBot(Bot):
    role = 'World class python & django developer who focuses on simplicity.'
    task = 'Return a django model python file based on the best practices provided.'
    guidelines = (
        Prompt()
        .heading('Best Practices')
        .file(BEST_PRACTICES)
    )
    intel_class = intel.PythonFileIntel

    def process(self, user_input: str, model_file: str) -> intel.PythonFileIntel:
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
    task = 'Identify all model fields and enrich the data.'
    guidelines = (
        Prompt()
        .list([
            'Be diligent. The user can be asking about many fields or a single field. We do not want to miss any field changes.',
            'Action is the step needed to take on the model file. Are we adding a field, editing an existing one or removing a field?.',
            'Field type specific django model fields (eg. character field, text field).',
            'Description is how the field relates to the model. Give context to make better technical decisions.',
            'Technical requirements are the arguments that go into the field.',
            'Focus on the user requests and use the model field for context to make better decisions.'
        ])
    )
    intel_class = intel.ModelActionIntel

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
    intel_class = intel.ModelActionIntel

    def process(self, user_input: str, model_file: str):
        # Find all fields and enrich the data
        model_fields_intel = ModelFieldIdentifierBot().process(user_input, model_file)

        programmer_bots = {
            'Choice Field Bot': ModelFieldGeneralProgrammerBot,
            'ForeignKey Bot': ModelFieldGeneralProgrammerBot,
            'Regular Bot (used for all other choices)': ModelFieldGeneralProgrammerBot
        }

        # Pass enriched data to specific field programmer bots
        for model_field in model_fields_intel.fields:
            field_programmer_bot = self.llm.decoder.prompt_to_value(
                prompt=model_field.to_prompt(),
                keys_description='Bots to program the model field.',
                keys_values=programmer_bots
            )

            model_file_intel = field_programmer_bot().process(user_input=model_field.to_prompt(), model_file=model_file)
            model_file = model_file_intel.python_file

        return model_file