from __future__ import annotations

from typing_extensions import Callable, TYPE_CHECKING

from django_spire.core.management.commands.spire_startapp_pkg.maps import generate_replacement_map

if TYPE_CHECKING:
    from pathlib import Path


class BaseTemplateProcessor:
    @staticmethod
    def apply_replacement(text: str, replacements: dict[str, str]) -> str:
        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    def replace_content(self, path: Path, components: list[str]) -> None:
        replacement = generate_replacement_map(components)

        with open(path, 'r', encoding='utf-8') as handle:
            content = handle.read()

        updated_content = self.apply_replacement(content, replacement)

        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(updated_content)

    def rename_file(self, path: Path, components: list[str]) -> None:
        replacement = generate_replacement_map(components)
        new_name = self.apply_replacement(path.name, replacement)

        if new_name != path.name:
            new_path = path.parent / new_name
            path.rename(new_path)

    def _process_files(
        self,
        directory: Path,
        components: list[str],
        pattern: str,
        file_filter: Callable[[Path], bool] | None = None
    ) -> None:
        for path in directory.rglob(pattern):
            if file_filter and not file_filter(path):
                continue

            self.replace_content(path, components)
            self.rename_file(path, components)


class AppTemplateProcessor(BaseTemplateProcessor):
    def replace_app_name(self, directory: Path, components: list[str]) -> None:
        self._process_files(
            directory,
            components,
            '*.template',
            lambda path: path.is_file()
        )

        self._process_files(
            directory,
            components,
            '*.py',
            lambda path: path.is_file()
        )

        self._rename_template_files(directory)

    def _rename_template_files(self, directory: Path) -> None:
        for template_file in directory.rglob('*.py.template'):
            new_name = template_file.name.replace('.py.template', '.py')
            new_path = template_file.parent / new_name
            template_file.rename(new_path)


class HTMLTemplateProcessor(BaseTemplateProcessor):
    def replace_template_names(self, directory: Path, components: list[str]) -> None:
        self._process_files(
            directory,
            components,
            '*.html'
        )
