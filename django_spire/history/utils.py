from __future__ import annotations

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django_spire.history.mixins import HistoryModelMixin


def add_form_activity(obj: HistoryModelMixin, pk: int, user: User) -> None:
    verb = (
        'created'
        if pk == 0 else 'updated'
    )

    information = (
        f'{user.get_full_name()} {verb} '
        f'{obj._meta.verbose_name} "{obj}".'
    )

    obj.add_activity(
        user=user,
        verb=verb,
        information=information
    )
