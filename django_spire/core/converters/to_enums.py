from __future__ import annotations

from enum import Enum


def django_choices_to_enums(
    class_name: str,
    choices: list[tuple[str, str]]
):
    choices_dict = {str(k).upper(): k for k, _ in choices}
    return Enum(class_name, choices_dict)
