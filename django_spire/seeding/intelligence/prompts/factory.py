from typing import Type

from django.db.models.base import Model

from dandy.llm import Prompt


class SeedingModelClassPromptFactory:

    def __init__(self, model_class: Type[Model]):
        self.model_class = model_class

    def objective_prompt(
            self,
            model_description: str,
            sector_description: str,
    ) -> Prompt:
        model_name = self.model_class._meta.verbose_name_plural.title()

        return (
            Prompt()
            .text(f'You are generating "{model_name}" that are described as "{model_description}".')
            .text(f'These {model_name} represent entities in our "{sector_description}" system.')
        )
