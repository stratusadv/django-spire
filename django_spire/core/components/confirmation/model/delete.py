from __future__ import annotations

from abc import ABC

from django_glue import Glue

from django_spire.core.components.confirmation.model.action import (
    BaseModelActionConfirmationComponent,
)


class BaseModelDeleteConfirmationComponent(BaseModelActionConfirmationComponent, ABC):
    """
    A :class:`BaseModelActionConfirmationComponent` worded and guarded as a
    delete: confirming needs ``DELETE`` access, and ``title``, ``message`` and
    ``confirm_label`` name the row and its model when left unset.

    A subclass deletes the row in ``perform_action()``.
    """

    template = 'django_spire/component/confirmation/model_delete.html'
    confirm_access = Glue.Access.DELETE


class ModelDeleteConfirmationComponent(BaseModelDeleteConfirmationComponent):
    """Deletes the row from the database, with the model's ``delete()``."""

    def perform_action(self) -> None:
        self.instance.delete()


class ModelSetDeletedConfirmationComponent(BaseModelDeleteConfirmationComponent):
    """Soft-deletes the row, with the ``set_deleted()`` of Spire's history mixin."""

    def perform_action(self) -> None:
        self.instance.set_deleted()
