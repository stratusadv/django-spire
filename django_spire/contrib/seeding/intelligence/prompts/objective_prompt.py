from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Prompt

if TYPE_CHECKING:
    from django.db.models import Model


def objective_prompt(
    model_class: type[Model],
    model_description: str,
    sector_description: str,
) -> Prompt:
    model_name = model_class._meta.verbose_name_plural.title()

    return (
        Prompt()
        .text(f'You are generating "{model_name}" that are described as "{model_description}".')
        .text(f'These {model_name} represent entities in our "{sector_description}" system.')
    )
