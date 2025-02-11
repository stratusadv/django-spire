from django.db.models import Field

from dandy.llm import Prompt


class SeedBotRulePromptFactory:

    def __init__(self, model_field: Field):
        self.model_field = model_field
        self.prompt = Prompt()

        self.build_prompt()


    def build_prompt(self) -> None:
        (
            self.prompt
            .text(f'"{self.model_field.name}" Field Rules:')
            .list(self.build_rules())
        )

    def build_rules(self) -> list[str]:
        rules = []

        # Todo: Need to create extendable pattern for different field types.
        if self.model_field.get_internal_type() in ['DateField', 'DateTimeField']:
            rules.append('Date Format: YYYY-MM-DD')

        rules.append(f'Is Required: {not bool(self.model_field.blank)}')
        rules.append(f'Is Unique: {self.model_field.unique}')

        if self.model_field.max_length:
            rules.append(f'Max Length: {self.model_field.max_length}')

        # Todo: Needs to be defined better.
        if self.model_field.choices:
            rules.append((
                'Use instruction context below to select from the following choices'
                'which are in a list of tuples in format (key, value)' 
                f': {self.model_field.choices}'
            ))

        return rules
