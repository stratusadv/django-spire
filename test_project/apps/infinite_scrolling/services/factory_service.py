from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from test_project.apps.infinite_scrolling.models import InfiniteScrolling


class InfiniteScrollingFactoryService(BaseDjangoModelService['InfiniteScrolling']):
    obj: InfiniteScrolling

    def save_model_obj(
        self,
        user: User,
        obj: InfiniteScrolling,
        **kwargs
    ) -> InfiniteScrolling:
        for key, value in kwargs.items():
            setattr(obj, key, value)

        obj.save()
        return obj
