from random import shuffle

from django.db.models import Model

from dandy.llm import Prompt


def hierarchical_selection_prompt(
    model_class: type[Model],
    self_reference_field: str,
    constraint: list[str]
) -> Prompt:
    # You must create/call a seeding function/prompt that
    # generates a "parent" or a "parent" must exist before
    # this prompt can be used.

    parent_instances = list(model_class.objects.all())
    shuffle(parent_instances)

    parent_constraints = []

    for instance in parent_instances:
        constraint_values = []

        for field in constraint:
            value = getattr(instance, field, None)
            constraint_values.append(f"{field}: {value!s}")

        parent_constraints.append(f'ID {instance.id}: {", ".join(constraint_values)}')

    model_name = model_class._meta.verbose_name.title()
    model_plural = model_class._meta.verbose_name_plural.title()

    constraint_descriptions = [f'`{field}`' for field in constraint]
    constraint_text = ' and '.join(constraint_descriptions)

    return (
        Prompt()
        .text(f'When creating {model_plural} with a `{self_reference_field}`, you must:')
        .list([
            f'Select one of the existing {model_plural} as the `{self_reference_field}`',
            f'Each child must have the same {constraint_text} as its `{self_reference_field}`',
        ])
        .line_break()

        .text(f'The available {model_plural} with their constraint values:')
        .list(parent_constraints)
        .line_break()

        .text(f'Do NOT create a parent. For example, no `{model_name}` should have `parent=null`.')
        .text(f'All rows should have a(n) {constraint_text}')
        .line_break()

        .text('Children MUST inherit these values from their parent. Do not modify them.')
    )
