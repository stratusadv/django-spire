from dandy import BaseIntel, BaseListIntel


class FilePathIntel(BaseIntel):
    file_path: str


class ModelFieldIntel(BaseIntel):
    field_name: str
    field_type: str
    description: str
    technical_requirements: str


class ModelFieldsIntel(BaseListIntel):
    fields: list[ModelFieldIntel]


class PythonFileIntel(BaseIntel):
    python_file: str
