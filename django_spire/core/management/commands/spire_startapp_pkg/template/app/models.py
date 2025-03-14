from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.breadcrumb.models import Breadcrumbs
from django_spire.history.mixins import HistoryModelMixin

from module import querysets


class SpireChildApp(HistoryModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.PlaceholderQuerySet().as_manager()

    def __str__(self):
        return self.name

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()

        crumbs.add_breadcrumb(
            'Placeholder',
            reverse('spireparentapp:spirechildapp:page:list')
        )

        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                str(self),
                reverse(
                    'spireparentapp:spirechildapp:page:detail',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    class Meta:
        verbose_name = 'SpireChildApp'
        verbose_name_plural = 'SpireChildApps'
        db_table = 'spireparentapp_spirechildapp'
