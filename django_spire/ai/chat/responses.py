import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List

from django.http import HttpRequest
from django.template.loader import render_to_string


class MessageResponseType(Enum):
    REQUEST = 'request'
    RESPONSE = 'response'
    LOADING_RESPONSE = 'loading_response'


@dataclass
class MessageResponse:
    request: HttpRequest
    type: MessageResponseType
    sender: str
    body: str

    @property
    def context_data(self) -> dict:
        return {
            'sender': self.sender,
            'body': self.body,
            'request': self.request
        }

    def _render_template_to_html_string(self, template_name: str, context_data: dict = None) -> str:
        return render_to_string(
            template_name=template_name,
            context={**self.context_data, **(context_data or {})},
        )

    def render_to_html_string(self, context_data: dict = None) -> str | None:
        if self.type == MessageResponseType.REQUEST:
            return self._render_template_to_html_string(
                'django_spire/ai/chat/message/request_message.html',
                context_data
            )
        elif self.type == MessageResponseType.RESPONSE:
            return self._render_template_to_html_string(
                'django_spire/ai/chat/message/response_message.html',
                context_data
            )
        elif self.type == MessageResponseType.LOADING_RESPONSE:
            return self._render_template_to_html_string(
                'django_spire/ai/chat/message/loading_response_message.html',
                context_data
            )
        else:
            return None

    def to_dict(self) -> dict:
        return {
            'type': self.type.value,
            'sender': self.sender,
            'body': self.body
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class MessageResponseGroup:
    message_responses: List[MessageResponse] = field(default_factory=list)

    def add_message_response(self, message_response: MessageResponse) -> None:
        self.message_responses.append(message_response)

    def render_to_html_string(self, context_data: dict = None) -> str:
        html_string = ''
        for message_response in self.message_responses:
            html_string += message_response.render_to_html_string(context_data)

        return html_string
