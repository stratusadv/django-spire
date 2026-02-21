from dandy import BaseIntel, BaseListIntel, Prompt


class FilePathIntel(BaseIntel):
    file_path: str


class ModelFieldIntel(BaseIntel):
    action: str
    field_name: str
    field_type: str
    description: str
    technical_requirements: str

    def to_prompt(self) -> Prompt:
        return (
            Prompt()
            .text(f'Action: {self.action}')
            .text(f'Field Name: {self.field_name}')
            .text(f'Field Type: {self.field_type}')
            .text(f'Description: {self.description}')
            .text(f'Technical Requirements: {self.technical_requirements}')
        )


class ModelFieldsIntel(BaseListIntel):
    fields: list[ModelFieldIntel]


class PythonFileIntel(BaseIntel):
    python_file: str
