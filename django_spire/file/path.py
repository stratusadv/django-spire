from __future__ import annotations

from dataclasses import dataclass

from django_spire.file.utils import random_64_char_token


@dataclass
class FilePathBuilder:
    base_folder: str
    app_name: str = 'Uncategorized'

    def __post_init__(self) -> None:
        if not self.base_folder:
            message = 'base_folder must not be empty.'
            raise ValueError(message)

    def build(self, name: str, extension: str, related_field: str = '') -> str:
        if not name:
            message = 'name must not be empty.'
            raise ValueError(message)

        if not extension:
            message = 'extension must not be empty.'
            raise ValueError(message)

        parts = [self.base_folder, self.app_name]

        if related_field:
            parts.append(related_field)

        token = random_64_char_token()
        parts.append(f'{token}_{name}.{extension}')

        return '/'.join(parts)
