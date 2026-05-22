from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from test_project.apps.sync.services.processor_service import SyncProcessorService
from test_project.apps.sync.services.transformation_service import SyncTransformationService

if TYPE_CHECKING:
    from test_project.apps.sync.models import Client


class SyncService(BaseDjangoModelService['Client']):
    obj: Client

    processor = SyncProcessorService()
    transformation = SyncTransformationService()
