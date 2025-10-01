from __future__ import annotations

from string import Template
from typing_extensions import Callable, TYPE_CHECKING

from django_spire.core.management.commands.spire_startapp_pkg.maps import generate_replacement_map

if TYPE_CHECKING:
    from pathlib import Path


class BaseTemplateProcessor:
    @staticmethod
    def render(text: str, replacements: dict[str, str]) -> str:
        template = Template(text)
        return template.safe_substitute(replacements)

    def rename_file(self, path: Path, components: list[str]) -> None:
        replacement = generate_replacement_map(components)
        new_name = self.render(path.name, replacement)

        if new_name != path.name:
            new_path = path.parent / new_name
            path.rename(new_path)

    def replace_content(self, path: Path, components: list[str]) -> None:
        replacement = generate_replacement_map(components)

        with open(path, 'r', encoding='utf-8') as handle:
            content = handle.read()

        updated_content = self.render(content, replacement)

        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(updated_content)

    def _process_files(
        self,
        directory: Path,
        components: list[str],
        pattern: str,
        filter: Callable[[Path], bool] | None = None
    ) -> None:
        for path in directory.rglob(pattern):
            if filter and not filter(path):
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
