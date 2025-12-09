from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Prompt

if TYPE_CHECKING:
    from django.db.models import Model


def foreign_key_selection_prompt(
    model_class: type[Model],
    related_model_class: type[Model]
) -> Prompt:
    model_name = model_class._meta.verbose_name.title()
    related_model_name = related_model_class._meta.verbose_name.title()
    related_model_plural = related_model_class._meta.verbose_name_plural.title()

    related_model_objects = related_model_class.objects.values_list('id', flat=True)

    return (
        Prompt()
        .heading(f'{related_model_name} Selection')
        .text(f'Each `{model_name}` must be associated with an existing `{related_model_name}`.')
        .text(f'The following "{related_model_plural}" are available to assign:')
        .list(related_model_objects)
    )
