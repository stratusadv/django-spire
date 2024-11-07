from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.breadcrumb.models import Breadcrumbs
from django_spire.history.mixins import HistoryModelMixin

from example.authentication import querysets


class Authentication(HistoryModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.AuthenticationQuerySet().as_manager()

    def __str__(self):
        return self.name

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()

        crumbs.add_breadcrumb(
            'Authentication',
            reverse('authentication:page:list')
        )

        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                str(self),
                reverse(
                    'authentication:page:detail',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    class Meta:
        verbose_name = 'Authentication'
        verbose_name_plural = 'Authentications'
        db_table = 'authentication'
