from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry


class BaseEntryImportService(BaseDjangoModelService['Entry'], ABC):
    obj: Entry

    @abstractmethod
    def import_doc(self, content: Any):
        raise NotImplementedError('import_doc method must be implemented.')
