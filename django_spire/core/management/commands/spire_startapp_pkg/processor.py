from __future__ import annotations

from string import Template
from typing import TYPE_CHECKING

from django_spire.core.management.commands.spire_startapp_pkg.maps import generate_replacement_map

if TYPE_CHECKING:
    from pathlib import Path

    from django_spire.core.management.commands.spire_startapp_pkg.filesystem import FileSystem


class TemplateEngine:
    """
    Renders template strings with variable replacements.

    This class uses Python's string.Template to safely substitute
    placeholders in template files with actual values.
    """

    def render(self, text: str, replacements: dict[str, str]) -> str:
        """
        Renders a template string by replacing placeholders with values.

        :param text: Template string containing ${variable} placeholders.
        :param replacements: Dictionary mapping placeholder names to their values.
        :return: Rendered string with all placeholders replaced.
        """

        template = Template(text)
        return template.safe_substitute(replacements)


class TemplateProcessor:
    """
    Processes template files for Django app generation.

    This class handles the replacement of placeholders in template files
    and manages file renaming based on user configuration.
    """

    def __init__(self, engine: TemplateEngine, filesystem: FileSystem):
        """
        Initializes the processor with an engine and file system.

        :param engine: Template engine for rendering strings.
        :param filesystem: File system for file operations.
        """

        self._engine = engine
        self._filesystem = filesystem

    def process_app_templates(
        self,
        directory: Path,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> None:
        """
        Processes all template files in an app directory.

        Replaces placeholders in .template files, renames them, and updates
        content in .py files based on user inputs.

        :param directory: Root directory containing template files.
        :param components: List of app path components.
        :param user_inputs: Optional dictionary of user-provided configuration values.
        """

        for file_path in self._filesystem.iterate_files(directory, '*.template'):
            self._process_file(file_path, components, user_inputs)

        for file_path in self._filesystem.iterate_files(directory, '*.py'):
            self._replace_content(file_path, components, user_inputs)
            self._rename_file(file_path, components, user_inputs)

        self._rename_template_files(directory)

    def process_html_templates(
        self,
        directory: Path,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> None:
        """
        Processes all HTML template files in a directory.

        Replaces placeholders in .template files and renames them to remove
        the .template extension.

        :param directory: Root directory containing HTML template files.
        :param components: List of app path components.
        :param user_inputs: Optional dictionary of user-provided configuration values.
        """

        for file_path in self._filesystem.iterate_files(directory, '*.template'):
            self._process_file(file_path, components, user_inputs)

        self._rename_template_files(directory)

    def _process_file(
        self,
        path: Path,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> None:
        """
        Processes a single template file.

        Replaces content placeholders and renames the file based on configuration.

        :param path: Path to the template file.
        :param components: List of app path components.
        :param user_inputs: Optional dictionary of user-provided configuration values.
        """

        self._replace_content(path, components, user_inputs)
        self._rename_file(path, components, user_inputs)

    def _rename_file(
        self,
        path: Path,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> None:
        """
        Renames a file by replacing placeholders in its filename.

        :param path: Current path of the file.
        :param components: List of app path components.
        :param user_inputs: Optional dictionary of user-provided configuration values.
        """

        replacement = generate_replacement_map(components, user_inputs)
        new_name = self._engine.render(path.name, replacement)

        if new_name != path.name:
            new_path = path.parent / new_name
            self._filesystem.rename(path, new_path)

    def _rename_template_files(self, directory: Path) -> None:
        """
        Removes .template extensions from all template files in a directory.

        :param directory: Directory to search for .template files.
        """

        for template_file in self._filesystem.iterate_files(directory, '*.template'):
            new_name = template_file.name.replace('.template', '')
            new_path = template_file.parent / new_name
            self._filesystem.rename(template_file, new_path)

    def _replace_content(
        self,
        path: Path,
        components: list[str],
        user_inputs: dict[str, str] | None = None
    ) -> None:
        """
        Replaces placeholders in a file's content.

        :param path: Path to the file to process.
        :param components: List of app path components.
        :param user_inputs: Optional dictionary of user-provided configuration values.
        """

        replacement = generate_replacement_map(components, user_inputs)
        content = self._filesystem.read_file(path)
        updated_content = self._engine.render(content, replacement)
        self._filesystem.write_file(path, updated_content)
