from __future__ import annotations

from dandy import BaseIntel, BaseListIntel, Prompt
from django_spire.contrib.programmer.models.enums import ModelActionEnum


class FilePathIntel(BaseIntel):
    file_path: str


# class ModelActionIntel(BaseIntel):
#     action: ModelActionEnum
#     target: str
#     context: str
#
#     def to_prompt(self) -> Prompt:
#         return (
#             Prompt()
#             .text(f'Action: {self.action}')
#             .text(f'Target: {self.target}')
#             .text(f'Context: {self.context}')
#         )
#

class ModelActionIntel(BaseIntel):
    name: str
    action: list[str] = None
    path: str | None = None
    file: str | None = None


class EnrichedUserInput(BaseIntel):
    model_name: str
    description: list[str]

    def to_prompt(self) -> Prompt:
        return (
            Prompt()
            .text(f'Model Name: {self.model_name}')
            .list([d for d in self.description])
        )

    def to_model_intel(self):
        pass


class EnrichedModelUserInput(BaseIntel):
    enriched_model_input: list[EnrichedUserInput]

    def to_prompt(self) -> Prompt:
        prompt = Prompt()

        for enriched_data in self.enriched_model_input:
            prompt.prompt(enriched_data.to_prompt())
            prompt.line_break()

        return prompt

    def model_names_to_prompt(self):
        return Prompt().list([f'{e.model_name} \n' for e in self.enriched_model_input])


class PythonFileIntel(BaseIntel):
    python_file: str


class HappyUser(BaseIntel):
    is_happy: bool
