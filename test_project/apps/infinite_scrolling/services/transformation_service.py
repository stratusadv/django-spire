from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from app.infinite_scrolling.models import InfiniteScrolling


class InfiniteScrollingTransformationService(BaseDjangoModelService['InfiniteScrolling']):
    obj: InfiniteScrolling
