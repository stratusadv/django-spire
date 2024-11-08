from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.breadcrumb.models import Breadcrumbs
from django_spire.history.mixins import HistoryModelMixin

from example.comment import querysets


class CommentExample(HistoryModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.CommentExampleQuerySet().as_manager()

    def __str__(self):
        return self.name

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()

        crumbs.add_breadcrumb(
            'Comment',
            reverse('comment:page:list')
        )

        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                str(self),
                reverse(
                    'comment:page:detail',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        db_table = 'example_comment'
