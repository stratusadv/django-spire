from __future__ import annotations

from pathlib import Path
from typing import Any, Type

from dandy import Bot, Prompt, BaseIntel
from dandy.cli.tui.tui import tui
from dandy.file.utils import get_directory_listing

from django_spire.contrib.programmer.models import intel


_RELATIVE_BASE_DIR = Path(Path(__file__).parent).resolve()
BEST_PRACTICES = Path(_RELATIVE_BASE_DIR, '../best_practices.md')


# Todo: This makes sense as a general bot...
class ModelFinderBot(Bot):
    role = 'Expert at searching file architectures to return the correct file.'
    task = 'Return the path to the located model file.'
    guidelines = (
        Prompt()
        .list([
            'Each django app has a models.py file.',
            'Our software architecture uses a nested hierarchy.'
        ])
    )
    intel_class = intel.ModelActionIntel

    def process(self, model_name: str) -> intel.ModelActionIntel:
        directories = (get_directory_listing(_RELATIVE_BASE_DIR.parent.parent.parent.resolve()))

        prompt = (
            Prompt()
            .heading('Model to Find')
            .text(model_name)
            .heading('Directories to Choose From')
            .list(directories)
        )
        model_action_intel = self.llm.prompt_to_intel(prompt=prompt, include_fields={'name', 'path'})

        if self.file.exists(model_action_intel.path):
            model_action_intel.file = self.file.read(model_action_intel.path)
        else:
            model_action_intel.file = ''

        return model_action_intel


class FeedBackBot(Bot):
    role = 'Expert in taking feedback and applying to improve the situation.'
    task = 'Take the users feedback and improve the response.'
    guidelines = (
        Prompt()
        .list([
            'Do you best to improve the response based on the users feedback.'
        ])
    )

    def process(
            self,
            response: str | Prompt,
            feedback: str | Prompt,
            bot: Type[Bot]
    ) -> Bot:

        prompt = (
            Prompt()
            .heading('Task')
            .text('The user wants to improve the response based on feedback.')
            .heading('Response')
            .text(response)
            .heading('Feedback')
            .text(feedback)
        )

        return bot().process(prompt=prompt)


class HappyUserBot(Bot):
    role = 'Decide if the user is happy with the response.'
    task = 'Return a boolean value based on if the user is ready to proceed.'
    guidelines = (
        Prompt()
        .list([
            'If the users is providing feedback, they are not ready to proceed.',
            'Only change the areas the user specifically mentions. Leave all remaining areas unchanged.'
        ])
    )
    intel_class = intel.HappyUser


