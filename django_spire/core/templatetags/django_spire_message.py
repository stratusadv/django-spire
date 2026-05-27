from __future__ import annotations

import json
import random
import string

from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from typing import Iterable

    from django.contrib.messages.storage.base import Message


register = template.Library()


@register.simple_tag()
def django_messages_to_json(messages: Iterable[Message]) -> str:
    return json.dumps([
        {
            'id': ''.join(random.choice(string.ascii_letters) for _ in range(8)),
            'message': message.message,
            'type': message.level_tag
        }
        for message in messages
    ])
