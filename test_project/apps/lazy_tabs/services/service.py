from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from test_project.apps.lazy_tabs.services.factory_service import LazyTabsFactoryService
from test_project.apps.lazy_tabs.services.intelligence_service import LazyTabsIntelligenceService
from test_project.apps.lazy_tabs.services.processor_service import LazyTabsProcessorService
from test_project.apps.lazy_tabs.services.transformation_service import LazyTabsTransformationService

if TYPE_CHECKING:
    from test_project.apps.lazy_tabs.models import LazyTabs


class LazyTabsService(BaseDjangoModelService['LazyTabs']):
    obj: LazyTabs

    intelligence = LazyTabsIntelligenceService()
    processor = LazyTabsProcessorService()
    factory = LazyTabsFactoryService()
    transformation = LazyTabsTransformationService()
