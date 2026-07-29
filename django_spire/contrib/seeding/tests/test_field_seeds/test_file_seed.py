from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest
from django.test import SimpleTestCase, override_settings

from django_spire.contrib.seeding.field.seed.file_seed import FileFieldSeed


class TestFileFieldSeed(SimpleTestCase):
    def setUp(self) -> None:
        self.temp_media_root = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_media_root)

    def test_file_created_on_init_seed_index(self):
        seed = FileFieldSeed()
        with override_settings(MEDIA_ROOT=str(self.temp_media_root)):
            value = seed.generate_value(-1)

        assert value == '.seeder/seeded_file.txt'
        assert (self.temp_media_root / '.seeder' / 'seeded_file.txt').exists()
        assert (self.temp_media_root / '.seeder' / 'seeded_file.txt').read_text() == 'Hello World'

    def test_returns_db_value_on_subsequent_calls(self):
        seed = FileFieldSeed()
        with override_settings(MEDIA_ROOT=str(self.temp_media_root)):
            seed.generate_value(-1)
            value_0 = seed.generate_value(0)
            value_5 = seed.generate_value(5)

        assert value_0 == '.seeder/seeded_file.txt'
        assert value_5 == '.seeder/seeded_file.txt'

    def test_error_when_media_root_is_none(self):
        seed = FileFieldSeed()
        with override_settings(MEDIA_ROOT=None), pytest.raises((TypeError, ValueError)):
            seed.generate_value(-1)

    def test_file_not_created_on_non_init_index(self):
        seed = FileFieldSeed()
        with override_settings(MEDIA_ROOT=str(self.temp_media_root)):
            value = seed.generate_value(0)

        assert value == '.seeder/seeded_file.txt'
        assert not (self.temp_media_root / '.seeder' / 'seeded_file.txt').exists()

    def test_idempotent_init_file_creation(self):
        seed = FileFieldSeed()
        with override_settings(MEDIA_ROOT=str(self.temp_media_root)):
            seed.generate_value(-1)
            seed.generate_value(-1)
            seed.generate_value(-1)

        assert (self.temp_media_root / '.seeder' / 'seeded_file.txt').exists()
        assert (self.temp_media_root / '.seeder' / 'seeded_file.txt').read_text() == 'Hello World'

    def test_does_not_overwrite_existing_file(self):
        seeder_dir = self.temp_media_root / '.seeder'
        seeder_dir.mkdir(parents=True, exist_ok=True)
        file_path = seeder_dir / 'seeded_file.txt'
        file_path.write_text('Existing Content')

        seed = FileFieldSeed()
        with override_settings(MEDIA_ROOT=str(self.temp_media_root)):
            seed.generate_value(-1)

        assert file_path.read_text() == 'Existing Content'
