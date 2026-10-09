from __future__ import annotations

from dataclasses import dataclass

from django.core.exceptions import ImproperlyConfigured

from django_spire.core.components.confirmation.model import (
    BaseModelDeleteConfirmationComponent,
    ModelSetDeletedConfirmationComponent,
)


@dataclass(frozen=True, kw_only=True)
class ComponentDeleteOptions:
    """
    A row is deleted through a confirmation component, shown in a modal.
    ``component`` is the confirmation, which soft-deletes the row with
    ``set_deleted()`` unless another is given. It fires ``confirmed`` with the
    row's ``pk``.
    """

    component: type[BaseModelDeleteConfirmationComponent] = ModelSetDeletedConfirmationComponent

    def __post_init__(self) -> None:
        if not isinstance(self.component, type) or not issubclass(
            self.component,
            BaseModelDeleteConfirmationComponent,
        ):
            message = (
                'ComponentDeleteOptions needs component to be a '
                'BaseModelDeleteConfirmationComponent class.'
            )
            raise ImproperlyConfigured(message)


@dataclass(frozen=True)
class PageDeleteOptions:
    """
    A row is deleted on a page of its own. ``url_name`` is the route that
    takes the row's key as ``pk``.

    The link carries a ``return_url`` for the page to send the user to
    afterwards: the route named by ``return_url_name``, or when that is left
    out, the address the list is shown at. A page that does not read
    ``return_url`` goes wherever it always does.
    """

    url_name: str
    return_url_name: str | None = None
