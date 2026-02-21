from pathlib import Path

from dandy import BaseIntel


class FilePathIntel(BaseIntel):
    file_path: str


class PythonFileIntel(BaseIntel):
    python_file: str
