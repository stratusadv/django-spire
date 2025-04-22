from django.db.models import Model

from typing_extensions import Type

from dandy.llm import Prompt


def objective_prompt(
    model_class: Type[Model],
    model_description: str,
    sector_description: str,
) -> Prompt:
    model_name = model_class._meta.verbose_name_plural.title()

    return (
        Prompt()
        .text(f'You are generating "{model_name}" that are described as "{model_description}".')
        .text(f'These {model_name} represent entities in our "{sector_description}" system.')
    )
