from typing import Union

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django_spire.comment.models import Comment


class CommentModelMixin(models.Model):
    comments = GenericRelation('comment.Comment', related_query_name='comment', editable=False)

    def add_comment(
            self,
            user: User,
            information: str,
            parent: Union[int, Comment, None] = None
    ):
        if isinstance(parent, Comment):
            parent = parent.pk

        return self.comments.create(information=information, user=user, parent_id=parent)

    class Meta:
        abstract = True
