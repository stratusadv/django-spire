from __future__ import annotations

import json
import random
import string

from django import template


register = template.Library()


@register.simple_tag()
def django_messages_to_json(messages):
    message_list = []

    for message in messages:
        message_list.append({
            'id': ''.join(random.choice(string.ascii_letters) for _ in range(8)),
            'message': message.message,
            'type': message.level_tag
        })

    return json.dumps(message_list)
