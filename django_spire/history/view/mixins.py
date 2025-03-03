from typing import TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django_spire.history.view.models import View

if TYPE_CHECKING:
    from django.contrib.auth.models import User

class ViewModelMixin(models.Model):
    views = GenericRelation(
        View,
        related_query_name='view',
        editable=False
    )

    def add_view(self, user: User) -> None:
        self.views.create(user=user)

    def is_viewed(self, user: User) -> None:
        return self.views.filter(user=user).exists()

    class Meta:
        abstract = True
