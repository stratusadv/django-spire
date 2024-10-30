from typing import Type

from django.contrib.auth.models import User

from django_spire.history.mixins import HistoryModelMixin


def add_form_activity(obj: Type[HistoryModelMixin], pk: int, user: User,):
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
