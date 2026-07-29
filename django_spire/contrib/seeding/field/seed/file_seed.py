from __future__ import annotations

from pathlib import Path
from typing import Any

from django.conf import settings

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class FileFieldSeed(BaseFieldSeed):
    def __init__(self) -> None:
        self._db_value = '.seeder/seeded_file.txt'

    def generate_value(self, seed_index: int) -> Any:
        if seed_index == -1:
            seeder_dir = Path(settings.MEDIA_ROOT) / '.seeder'
            seeder_dir.mkdir(parents=True, exist_ok=True)

            file_path = seeder_dir / 'seeded_file.txt'
            if not file_path.exists():
                file_path.write_text('Hello World')

        return self._db_value
