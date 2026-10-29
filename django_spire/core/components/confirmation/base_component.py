from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from django_glue import Glue

from django_spire.core.components.confirmation.exceptions import ConfirmationRefusedError


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

    An action that cannot be performed, because its row changed while the
    prompt was open say, raises ``ConfirmationRefusedError``: ``confirmed`` is
    not fired, and the prompt stays open and shows the error's message.

    ``confirm_access`` is the access the user needs in order to confirm.
    """

    template = 'django_spire/component/confirmation/confirmation.html'
    confirm_access: ClassVar[Glue.Access] = Glue.Access.VIEW

    title: str | None = Glue.ComponentParameter(None)
    message: str | None = Glue.ComponentParameter(None)
    confirm_label: str | None = Glue.ComponentParameter(None)

    cancelled = Glue.event()
    confirmed = Glue.event()

    @abstractmethod
    def on_confirm(self) -> dict[str, Any]:
        """
        Perform the confirmed action and return the detail of ``confirmed``, or
        raise ``ConfirmationRefusedError`` to leave the prompt open with its message.
        """

    @Glue.attr(required_access=lambda component: component.confirm_access, skip_rerender=True)
    def confirm(self) -> Glue.Response | None:
        try:
            detail = self.on_confirm()
        except ConfirmationRefusedError as error:
            return Glue.Response(messages=[Glue.Response.Message.error(str(error))])

        self.confirmed(**detail)

        return None
