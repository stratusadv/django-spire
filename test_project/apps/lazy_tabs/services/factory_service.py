from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from test_project.apps.lazy_tabs.models import LazyTabs


class LazyTabsFactoryService(BaseDjangoModelService['LazyTabs']):
    obj: LazyTabs

    def save_model_obj(
        self,
        user: User,
        obj: LazyTabs,
        **kwargs
    ) -> LazyTabs:
        for key, value in kwargs.items():
            setattr(obj, key, value)

        obj.save()
        return obj
