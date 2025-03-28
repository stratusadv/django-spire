from enum import Enum


def django_choices_to_enums(
        class_name: str,
        choices: list[tuple[str, str]]
):
    return Enum(class_name, {k: k for k, v in choices})

