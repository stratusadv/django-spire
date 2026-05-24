from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from test_project.app.file.services.factory_service import FileExampleFactoryService
from test_project.app.file.services.processor_service import FileExampleProcessorService
from test_project.app.file.services.transformation_service import FileExampleTransformationService

if TYPE_CHECKING:
    from test_project.app.file.models import FileExample


class FileExampleService(BaseDjangoModelService['FileExample']):
    obj: FileExample

    factory = FileExampleFactoryService()
    processor = FileExampleProcessorService()
    transformation = FileExampleTransformationService()
