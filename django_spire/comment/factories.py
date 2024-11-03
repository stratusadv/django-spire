from __future__ import annotations

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.db.models import Model


def create_or_update_comment(obj: Model, user: User, information: str):
    pass
