from __future__ import annotations

from pathlib import Path
from typing import Any

from django.conf import settings

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class FileFieldSeed(BaseFieldSeed):
    def __init__(self, upload_to: str | None = None) -> None:
        if upload_to:
            self._seeding_dir = Path(upload_to, '.seeding')
        else:
            self._seeding_dir = '.seeding'

        self._seeding_txt_file = 'seeded_file.txt'

        self._seeding_file_path = Path(self._seeding_dir, self._seeding_txt_file)

    def generate_value(self, seed_index: int) -> Any:
        if seed_index == -1:
            seeder_dir = Path(settings.MEDIA_ROOT) / self._seeding_dir
            seeder_dir.mkdir(parents=True, exist_ok=True)

            file_path = seeder_dir / 'seeded_file.txt'
            if not file_path.exists():
                file_path.write_text('Hello World')

        return self._seeding_file_path
