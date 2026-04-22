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
        is_new = not obj.pk

        for key, value in kwargs.items():
            setattr(obj, key, value)

        obj.save()

        verb = 'created' if is_new else 'updated'

        obj.add_activity(
            user=user,
            verb=verb,
            information=f'{user.get_full_name()} {verb} {obj.name}.'
        )

        return obj
