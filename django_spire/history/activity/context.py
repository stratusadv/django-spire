from __future__ import annotations

from contextvars import ContextVar, Token
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import User


_current_user: ContextVar[User | None] = ContextVar('_current_user', default=None)


def get_current_user() -> User | None:
    return _current_user.get()


def set_current_user(user: User | None) -> Token[User | None]:
    return _current_user.set(user)


def reset_current_user(token: Token[User | None]) -> None:
    _current_user.reset(token)
