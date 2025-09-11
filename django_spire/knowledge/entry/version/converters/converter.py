from __future__ import annotations

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from django_spire.file.models import File
    from django_spire.knowledge.entry.version.models import EntryVersion
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


class BaseConverter(ABC):
    def __init__(self, entry_version: EntryVersion):
        self.entry_version = entry_version

    @abstractmethod
    def convert_file_to_blocks(self, file: File) -> list[EntryVersionBlock]:
        raise NotImplementedError
