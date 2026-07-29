from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import SimpleTestCase, override_settings

from django_spire.contrib.seeding.field.seed.file_seed import FileFieldSeed


def _storage_config(media_root: str) -> dict:
    return {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
            'OPTIONS': {'location': media_root},
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }


class TestFileFieldSeed(SimpleTestCase):
    def setUp(self) -> None:
        self.temp_media_root = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_media_root)

    def _override(self) -> override_settings:
        return override_settings(STORAGES=_storage_config(str(self.temp_media_root)))

    def _assert_seeding_file_exists(self, content: str = 'Hello World') -> None:
        assert default_storage.exists('.seeding/seeded_file.txt')
        with default_storage.open('.seeding/seeded_file.txt') as f:
            assert f.read().decode() == content

    def test_file_created_on_init_seed_index(self) -> None:
        seed = FileFieldSeed()
        with self._override():
            value = seed.generate_value(-1)
            self._assert_seeding_file_exists()

        assert value == Path('.seeding/seeded_file.txt')

    def test_returns_db_value_on_subsequent_calls(self) -> None:
        seed = FileFieldSeed()
        with self._override():
            seed.generate_value(-1)
            value_0 = seed.generate_value(0)
            value_5 = seed.generate_value(5)

        assert value_0 == Path('.seeding/seeded_file.txt')
        assert value_5 == Path('.seeding/seeded_file.txt')

    def test_file_not_created_on_non_init_index(self) -> None:
        seed = FileFieldSeed()
        with self._override():
            value = seed.generate_value(0)
            assert not default_storage.exists('.seeding/seeded_file.txt')

        assert value == Path('.seeding/seeded_file.txt')

    def test_idempotent_init_file_creation(self) -> None:
        seed = FileFieldSeed()
        with self._override():
            seed.generate_value(-1)
            seed.generate_value(-1)
            seed.generate_value(-1)
            self._assert_seeding_file_exists()

    def test_does_not_overwrite_existing_file(self) -> None:
        with self._override():
            default_storage.save(
                '.seeding/seeded_file.txt', ContentFile(b'Existing Content')
            )

            seed = FileFieldSeed()
            seed.generate_value(-1)

            self._assert_seeding_file_exists('Existing Content')
