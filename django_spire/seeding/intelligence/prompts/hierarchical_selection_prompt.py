from django.db.models import Model

from dandy.llm import Prompt


def hierarchical_selection_prompt(
    model_class: type[Model],
    self_reference_field: str,
    constraint: list[str]
) -> Prompt:
    parent_instances = model_class.objects.all()

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

        .text(f'You may create ONE {model_name} where `parent=null`. All other rows should have a(n) {constraint_text}')
        .line_break()

        .text('Children MUST inherit these values from their parent. Do not modify them.')
    )
