from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from test_project.apps.infinite_scrolling.services.factory_service import InfiniteScrollingFactoryService
from test_project.apps.infinite_scrolling.services.intelligence_service import InfiniteScrollingIntelligenceService
from test_project.apps.infinite_scrolling.services.processor_service import InfiniteScrollingProcessorService
from test_project.apps.infinite_scrolling.services.transformation_service import InfiniteScrollingTransformationService

if TYPE_CHECKING:
    from test_project.apps.infinite_scrolling.models import InfiniteScrolling


class InfiniteScrollingService(BaseDjangoModelService['InfiniteScrolling']):
    obj: InfiniteScrolling

    intelligence = InfiniteScrollingIntelligenceService()
    processor = InfiniteScrollingProcessorService()
    factory = InfiniteScrollingFactoryService()
    transformation = InfiniteScrollingTransformationService()
