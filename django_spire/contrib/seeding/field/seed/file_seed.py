from __future__ import annotations

from pathlib import PurePath
from typing import Any

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class FileFieldSeed(BaseFieldSeed):
    def __init__(self, upload_to: str | None = None) -> None:
        if upload_to:
            self._seeding_dir = PurePath(upload_to, '.seeding')
        else:
            self._seeding_dir = PurePath('.seeding')

        self._seeding_txt_file = 'seeded_file.txt'
        self._seeding_file_path = self._seeding_dir / self._seeding_txt_file

    def generate_cache_key(self) -> str:
        return str(self._seeding_file_path)

    def generate_value(self, seed_index: int) -> Any:
        if seed_index == -1:
            path = str(self._seeding_file_path)

            if not default_storage.exists(path):
                default_storage.save(path, ContentFile(b'Hello World'))

        return str(self._seeding_file_path)
