from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

    from django.contrib.auth.models import User
    from django.db import models


    DeleteActivityEntry = tuple[type[models.Model], int, str]


ACTIVITY_VERB_ATTRIBUTE = '_activity_verb'

_current_user: ContextVar[User | None] = ContextVar('_current_user', default=None)

_delete_activity_entries: ContextVar[list[DeleteActivityEntry] | None] = ContextVar(
    '_delete_activity_entries',
    default=None
)


@contextmanager
def activity_user(user: User | None) -> Iterator[None]:
    token = set_current_user(user)

    try:
        yield
    finally:
        reset_current_user(token)


def get_current_user() -> User | None:
    user = _current_user.get()

    if user is None:
        return None

    if not user.is_authenticated:
        return None

    return user


def set_current_user(user: User | None) -> Token[User | None]:
    return _current_user.set(user)


def reset_current_user(token: Token[User | None]) -> None:
    _current_user.reset(token)


def get_delete_activity_entries() -> list[DeleteActivityEntry] | None:
    return _delete_activity_entries.get()


def start_delete_activity_collection() -> Token[list[DeleteActivityEntry] | None]:
    return _delete_activity_entries.set([])


def reset_delete_activity_collection(
    token: Token[list[DeleteActivityEntry] | None]
) -> None:
    _delete_activity_entries.reset(token)
