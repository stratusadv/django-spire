from dandy.llm import Prompt
from django.db.models.enums import TextChoices
from django.db.models.fields import Field


def model_field_choices_prompt(
        model_field: Field,
        choices: TextChoices,
) -> Prompt:
    model_name = model_field.field.model.__name__
    field_name = model_field.field.name
    return (
        Prompt()
        .heading(f'Generate values for {field_name} in {model_name} model')
        .text(f'The value for the {field_name} field should only be selected from the following list of choices.')
        .list([choice[0] for choice in choices])
    )
