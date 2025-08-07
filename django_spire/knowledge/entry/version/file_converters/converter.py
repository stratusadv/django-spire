from __future__ import annotations

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from django_spire.file.models import File
    from django_spire.knowledge.entry.version.models import EntryVersion
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class BaseFileConverter(ABC):
    def __init__(self, file: File) -> None:
        self.file = file

    @abstractmethod
    def convert_to_model_objects(
            self,
            entry_version: EntryVersion
    ) -> list[EntryVersionBlock]:
        raise NotImplementedError
