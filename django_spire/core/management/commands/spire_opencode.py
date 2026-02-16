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

        # --- WARNING & MANIFEST ---
        self.stdout.write(self.style.WARNING('!' * 60))
        self.stdout.write(self.style.WARNING('WARNING: DUPLICATE CONTENT WILL BE OVERWRITTEN'))
        self.stdout.write(self.style.WARNING(
            'This command copies files from Spire to your project root.\n'
            'If you have existing agents or skills with the same names,\n'
            'their directories will be merged and existing files OVERWRITTEN.'
        ))
        self.stdout.write(self.style.WARNING('!' * 60))

        self.stdout.write('\nThe following assets have been found in the Spire package:')

        # List Agents found in source
        self._preview_directory_contents(source_pkg_dir / 'agents', 'AGENTS')

        # List Skills found in source
        self._preview_directory_contents(source_pkg_dir / 'skills', 'SKILLS')


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

        if import_agents:
            self._sync_directory(
                source_pkg_dir / 'agents',
                dest_root_dir / 'agents'
            )

        if import_skills:
            self._sync_directory(
                source_pkg_dir / 'skills',
                dest_root_dir / 'skills'
            )

        self.stdout.write(self.style.SUCCESS('\nOperation complete.'))

    def _preview_directory_contents(self, path: Path, label: str):
        """Helper to list the immediate children of a directory for preview."""
        if not path.exists():
            return

        self.stdout.write(self.style.SUCCESS(f'\n[{label}]'))

        items = sorted(path.iterdir())
        if not items:
            self.stdout.write('  (Empty directory)')
            return

        for item in items:
            # Differentiate visually between folders and files
            prefix = "📂" if item.is_dir() else "📄"
            self.stdout.write(f'  - {prefix} {item.name}')

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

