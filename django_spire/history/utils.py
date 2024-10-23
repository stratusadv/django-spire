from typing import Type
from django_spire.history.mixins import HistoryModelMixin
from django.contrib.auth.models import User


def add_form_activity(obj: Type[HistoryModelMixin], pk: int, user: User,):
    verb = 'updated' if pk != 0 else 'created'
    obj.add_activity(
        user=user,
        verb=verb,
        information=f'{user.get_full_name()} {verb} {obj._meta.verbose_name} "{obj}".'
    )
