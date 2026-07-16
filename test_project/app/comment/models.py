from __future__ import annotations

from django.db import models

from django_spire.comment.mixins import CommentModelMixin
from django_spire.history.mixins import HistoryModelMixin

from test_project.app.comment import querysets


class CommentExample(HistoryModelMixin, CommentModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.CommentExampleQuerySet().as_manager()

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        db_table = 'test_project_comment'

    def __str__(self) -> str:
        return self.name

