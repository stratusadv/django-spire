from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from django.db.models import Model  # noqa: TC002
from django_glue import Glue

from django_spire.core.components.confirmation.base import BaseConfirmationComponent


class BaseModelActionConfirmationComponent(BaseConfirmationComponent, ABC):
    """
    A :class:`BaseConfirmationComponent` for one action on one model row.

    Built with the row, as ``instance=``, it works for any model. Confirming
    performs the action with ``perform_action()``, which a subclass writes,
    and fires ``confirmed`` with the row's ``pk``.
    """

    @Glue.ComponentParameter
    def instance(self, model: type[Model], pk: int) -> Model:
        return model._default_manager.get(pk=pk)

    @property
    def model_name(self) -> str:
        return str(self.instance._meta.verbose_name)

    @abstractmethod
    def perform_action(self) -> None:
        """Perform the confirmed action on ``self.instance``."""

    def on_confirm(self) -> dict[str, Any]:
        pk = self.instance.pk

        self.perform_action()

        return {'pk': pk}
