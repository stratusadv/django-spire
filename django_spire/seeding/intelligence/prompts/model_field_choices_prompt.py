from typing import List

from dandy.llm import Prompt

def model_field_choices_prompt(
        model_field: str,
        choices_list: List[str],
) -> Prompt:
    model_name = model_field.field.model._meta.verbose_name
    field_name = model_field.field.attname
    return (
        Prompt()
        .heading(f'Generate values for {field_name} in {model_name} model')
        .text(f'The value for the {field_name} field should only be selected from the following list of choices.')
        .list(choices_list)
    )
