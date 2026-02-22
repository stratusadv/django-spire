from __future__ import annotations


from dandy import BaseIntel, Prompt


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

class ModelIntel(BaseIntel):
    name: str
    actions: list[str] = None
    path: str | None = None
    file: str | None = None

    def find(self):
        from django_spire.contrib.programmer.models.bots.general_bots import ModelFinderBot
        model_intel = ModelFinderBot().process(self.name)
        self.path = model_intel.path
        self.file = model_intel.file

    def to_prompt(self):
        return (
            Prompt()
            .text(f'Name: {self.name}')
            .list([a for a in self.actions])
        )

class ModelsIntel(BaseIntel):
    models: list[ModelIntel]

    def to_prompt(self) -> Prompt:
        prompt = Prompt()
        for model in self.models:
            prompt.prompt(model.to_prompt())
        return prompt

    def names_to_prompt(self):
        return Prompt().list([m.name for m in self.models])



class PythonFileIntel(BaseIntel):
    python_file: str


class HappyUser(BaseIntel):
    is_happy: bool
