from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from django_glue import Glue
from django_glue.access import GlueAccess  # noqa: TC002


class BaseConfirmationComponent(Glue.Component, ABC):
    """
    Asks the user to confirm one action.

    Subclasses perform the action in ``on_confirm()``. The prompt is worded
    when the component is built, with ``title``, ``message`` and
    ``confirm_label``; one left unset keeps the template's own wording::

        ArchiveConfirmationComponent(title='Archive this report?', confirm_label='Archive')

    A subclass that needs markup, such as an icon, extends the template's
    ``confirmation_title``, ``confirmation_message`` and
    ``confirmation_button`` blocks. ``confirmation_button`` holds the whole
    confirm button.

    The component does not know what it is shown in, so it closes nothing.
    Whoever shows it listens for ``confirmed``, which carries what
    ``on_confirm()`` returned, and for ``cancelled``, and puts it away.
    Cancelling does nothing on the server, so the template raises
    ``cancelled`` in the browser.

    ``confirm_access`` is the access the user needs in order to confirm.
    """

    template = 'django_spire/component/confirmation/base.html'
    confirm_access: ClassVar[GlueAccess] = Glue.Access.VIEW

    title: str | None = Glue.ComponentParameter(None)
    message: str | None = Glue.ComponentParameter(None)
    confirm_label: str | None = Glue.ComponentParameter(None)

    cancelled = Glue.event()
    confirmed = Glue.event()

    @abstractmethod
    def on_confirm(self) -> dict[str, Any]:
        """Perform the confirmed action and return the detail of ``confirmed``."""

    @Glue.attr(required_access=lambda component: component.confirm_access, skip_rerender=True)
    def confirm(self) -> None:
        self.confirmed(**self.on_confirm())
