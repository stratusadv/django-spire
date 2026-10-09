from __future__ import annotations

from typing import Any

from django.db.models import Model  # noqa: TC002
from django_glue import Glue

from django_spire.core.components.confirmation.base import BaseConfirmationComponent


class ModelDeleteConfirmationComponent(BaseConfirmationComponent):
    """
    A :class:`BaseConfirmationComponent` that deletes one model row.

    Built with the row to delete, as ``model_obj=``, it works for any model
    without a subclass. Confirming needs ``DELETE`` access, soft-deletes the
    row with ``set_deleted()`` and fires ``confirmed`` with its ``pk``.
    Override ``on_confirm()`` to delete some other way.

    Left unset, ``title``, ``message`` and ``confirm_label`` name the row and
    its model.
    """

    template = 'django_spire/component/confirmation/model_delete.html'
    confirm_access = Glue.Access.DELETE

    @Glue.ComponentParameter
    def model_obj(self, model: type[Model], pk: int) -> Model:
        return model._default_manager.get(pk=pk)

    @property
    def model_name(self) -> str:
        return str(self.model_obj._meta.verbose_name)

    def on_confirm(self) -> dict[str, Any]:
        self.model_obj.set_deleted()

        return {'pk': self.model_obj.pk}
