from __future__ import annotations

import sass
import time

from threading import Thread
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class ScssWatcher:
    def __init__(self, scss_dir: Path, css_dir: Path) -> None:
        self.scss_dir = scss_dir
        self.css_dir = css_dir
        self.file_mtimes = {}
        self.running = False
        self.thread = None

    def compile_scss(self, scss_file: Path) -> None:
        css_file = self.css_dir / scss_file.name.replace('.scss', '.css')

        try:
            with open(scss_file, 'r', encoding='utf-8') as f:
                scss_content = f.read()

            if not scss_content.strip():
                self.css_dir.mkdir(parents=True, exist_ok=True)

                with open(css_file, 'w', encoding='utf-8') as f:
                    f.write('')

                print(f'Compiled (empty): {scss_file.name} -> {css_file.name}')
                return

            css_content = sass.compile(
                string=scss_content,
                output_style='compressed',
                include_paths=[str(self.scss_dir)]
            )

            self.css_dir.mkdir(parents=True, exist_ok=True)

            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(css_content)

            print(f'Compiled: {scss_file.name} -> {css_file.name}')
        except Exception as e:
            print(f'Error compiling {scss_file.name}: {e}')

    def watch(self) -> None:
        while self.running:
            try:
                for scss_file in self.scss_dir.glob('*.scss'):
                    if scss_file.name.startswith('_'):
                        continue

                    current_mtime = scss_file.stat().st_mtime

                    if scss_file not in self.file_mtimes or self.file_mtimes[scss_file] < current_mtime:
                        self.compile_scss(scss_file)
                        self.file_mtimes[scss_file] = current_mtime

                time.sleep(0.5)
            except Exception as e:
                print(f'Error in SCSS watcher: {e}')
                time.sleep(1)

    def start(self) -> None:
        if self.running:
            return

        self.running = True
        self.thread = Thread(target=self.watch, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.running = False

        if self.thread:
            self.thread.join(timeout=2)
