from dandy import BaseIntel, BaseListIntel, Prompt


class FilePathIntel(BaseIntel):
    file_path: str


class EnrichedUserInput(BaseIntel):
    model_name: str
    # ooohhhh, I can add model path here then we have it where we need it :)
    # model_path: str
    # model_file: str
    description: list[str]
    
    def to_prompt(self) -> Prompt:
        return (
            Prompt()
            .text(f'Model Name: {self.model_name}')
            .list([d for d in self.description])
        )


class EnrichedModelUserInput(BaseIntel):
    enriched_model_input: list[EnrichedUserInput]

    def to_prompt(self) -> Prompt:
        prompt = Prompt()

        for enriched_data in self.enriched_model_input:
            prompt.prompt(enriched_data.to_prompt())
            prompt.line_break()

        return prompt


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


class HappyUser(BaseIntel):
    is_happy: bool
