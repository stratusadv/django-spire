from __future__ import annotations

from typing import TYPE_CHECKING

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


if TYPE_CHECKING:
    from typing import Any


class Command(BaseCommand):
    help = 'Download skills and agents for opencode.'

    def handle(self, *args: Any, **kwargs: Any) -> None:
        current_cmd_dir = Path(__file__).resolve().parent
        source_pkg_dir = current_cmd_dir / 'spire_opencode_pkg'
        dest_root_dir = settings.BASE_DIR

        if not source_pkg_dir.exists():
            raise CommandError(f"Could not find source package at: {source_pkg_dir}")

        raw_config = input('Do you want to import opencode.json config? (y/n) (default: n) -> ').strip().lower()
        import_config = raw_config == 'y'

        raw_agents = input('Do you want to import agents? (y/n) (default: y) -> ').strip().lower()
        import_agents = raw_agents != 'n'

        raw_skills = input('Do you want to import skills? (y/n) (default: y) -> ').strip().lower()
        import_skills = raw_skills != 'n'

        if import_config:
            src_file = source_pkg_dir / 'opencode.json'
            dest_file = dest_root_dir / 'opencode.json'

            should_copy = True

            if dest_file.exists():
                self.stdout.write(self.style.WARNING(f'[!] Configuration file already exists at: {dest_file}'))
                overwrite = input('Do you want to overwrite it? (y/n) (default: n) -> ').strip().lower()

                if overwrite != 'y':
                    should_copy = False
                    self.stdout.write(self.style.WARNING('[!] Skipped config overwrite.'))

            if should_copy:
                shutil.copy2(src_file, dest_file)
                self.stdout.write(self.style.SUCCESS(f'[✔] Copied opencode.json to {dest_file}'))
        #
        # if import_agents:
        #     self._sync_directory(
        #         source_pkg_dir / 'agents',
        #         dest_root_dir / 'agents'
        #     )
        #
        # if import_skills:
        #     self._sync_directory(
        #         source_pkg_dir / 'skills',
        #         dest_root_dir / 'skills'
        #     )
        #
        # self.stdout.write(self.style.SUCCESS('\nOperation complete.'))


    def _sync_directory(self, src_path: Path, dest_path: Path):
        """
            Helper to copy a directory tree, overwriting existing files.
        """
        if not src_path.exists():
            self.stdout.write(self.style.WARNING(f'[!] Source directory not found: {src_path}'))
            return

        # Create destination if it doesn't exist
        if not dest_path.exists():
            dest_path.mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f'[+] Created directory: {dest_path}'))

        # Copy files using shutil.copytree with dirs_exist_ok=True (Python 3.8+)
        # This recursively copies the folder and overwrites files if they exist
        try:
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f'[✔] Synced contents of {src_path.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[X] Failed to sync {src_path.name}: {e}'))

