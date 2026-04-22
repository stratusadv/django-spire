from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from test_project.apps.lazy_tabs.models import LazyTabs


class LazyTabsTransformationService(BaseDjangoModelService['LazyTabs']):
    obj: LazyTabs
