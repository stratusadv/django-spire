from __future__ import annotations

import shutil

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Iterator


class FileSystem:
    """
    Implementation of file system operations for app generation.

    This class provides concrete implementations of file system operations
    needed to create directories, copy templates, and manage files.
    """

    def copy_tree(self, src: Path, dst: Path) -> None:
        """
        Copies an entire directory tree from source to destination.

        Ignores Python cache directories and compiled files during the copy.

        :param src: Source directory path to copy from.
        :param dst: Destination directory path to copy to.
        """

        shutil.copytree(
            src,
            dst,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns('__pycache__', '*.pyc')
        )

    def create_directory(self, path: Path) -> None:
        """
        Creates a directory and all necessary parent directories.

        :param path: Directory path to create.
        """

        path.mkdir(parents=True, exist_ok=True)

    def exists(self, path: Path) -> bool:
        """
        Checks if a path exists on the file system.

        :param path: Path to check for existence.
        :return: True if the path exists, False otherwise.
        """

        return path.exists()

    def has_content(self, path: Path) -> bool:
        """
        Checks if a directory exists and contains any files or subdirectories.

        :param path: Directory path to check.
        :return: True if the directory exists and has content, False otherwise.
        """

        return self.exists(path) and any(path.iterdir())

    def iterate_files(self, path: Path, pattern: str) -> Iterator[Path]:
        """
        Recursively finds all files matching a pattern in a directory.

        :param path: Directory path to search within.
        :param pattern: Glob pattern to match files (e.g., '*.py', '*.template').
        :return: Iterator of matching file paths.
        """

        return path.rglob(pattern)

    def read_file(self, path: Path) -> str:
        """
        Reads the entire contents of a text file.

        :param path: File path to read.
        :return: File contents as a string.
        """

        with open(path, 'r', encoding='utf-8') as handle:
            return handle.read()

    def rename(self, old: Path, new: Path) -> None:
        """
        Renames a file or directory.

        :param old: Current path of the file or directory.
        :param new: New path for the file or directory.
        """

        old.rename(new)

    def write_file(self, path: Path, content: str) -> None:
        """
        Writes content to a text file.

        :param path: File path to write to.
        :param content: String content to write to the file.
        """

        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(content)
