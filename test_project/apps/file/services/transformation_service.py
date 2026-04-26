from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from test_project.apps.file.models import FileExample


class FileExampleTransformationService(BaseDjangoModelService['FileExample']):
    obj: FileExample
