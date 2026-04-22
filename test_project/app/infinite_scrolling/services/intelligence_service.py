from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from test_project.apps.infinite_scrolling.models import InfiniteScrolling


class InfiniteScrollingIntelligenceService(BaseDjangoModelService['InfiniteScrolling']):
    obj: InfiniteScrolling
