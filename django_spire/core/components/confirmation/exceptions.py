from __future__ import annotations

from django_spire.exceptions import DjangoSpireError


class ConfirmationRefusedError(DjangoSpireError):
    """The confirmed action was not performed; its message tells the user why."""
