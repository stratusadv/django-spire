from __future__ import annotations

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from django_spire.file.models import File
    from django_spire.knowledge.entry.version.models import EntryVersion
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class BaseFileConverter(ABC):
    def __init__(self, file: File, entry_version: EntryVersion):
        self.file = file
        self.entry_version = entry_version

    @abstractmethod
    def convert_to_model_objects(self) -> list[EntryVersionBlock]:
        raise NotImplementedError
