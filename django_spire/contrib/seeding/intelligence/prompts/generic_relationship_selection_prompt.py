from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

from dandy import Prompt

if TYPE_CHECKING:
    from django.db.models import Model


def generic_relationship_selection_prompt(
    model_class: type[Model],
    related_model_classes: list[type[Model]]
) -> Prompt:
    related_model_classes_map = {
        related_model_class._meta.verbose_name.title(): {
            'content_type_id': ContentType.objects.get_for_model(related_model_class).id,
            'queryset': related_model_class.objects.all(),
        }
        for related_model_class in related_model_classes
    }

    model_name = model_class._meta.verbose_name.title()
    related_model_class_names = list(related_model_classes_map.keys())

    related_model_object_id_to_content_type_id_map = {}

    for related_model_class_map in related_model_classes_map.values():
        for related_model_object in related_model_class_map['queryset']:
            model_class_name = related_model_object._meta.verbose_name.title()
            content_type_id = related_model_classes_map[model_class_name]['content_type_id']
            related_model_object_id_to_content_type_id_map[str(related_model_object.id)] = content_type_id

    return (
        Prompt()
        .heading('Generic Related Model Selection')
        .text(f'Each `{model_name}` must be linked to an existing entity.')
        .text('The following entity types are available to use:')
        .list(related_model_class_names)
        .line_break()
        .text('The following entities are available to assign (IDs listed):')
        .unordered_random_list(list(related_model_object_id_to_content_type_id_map.keys()))
        .line_break()
        .text('Use the following mapping to correctly set `content_type_id` based on the selected entity ID:')
        .dict(related_model_object_id_to_content_type_id_map)
        .line_break()
        .text(f'The `object_id` is the ID of the entity this `{model_name}` is associated with.')
    )
