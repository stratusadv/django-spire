from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django_spire.ai.chat.models import Chat

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def create_test_chat(user: Any[User]) -> Chat:
    return Chat.objects.create(
        user=user,
        name='New Exciting Chat!'
    )
