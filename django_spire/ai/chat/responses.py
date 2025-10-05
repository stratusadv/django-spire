from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django.template.loader import render_to_string

from django_spire.ai.chat.choices import MessageResponseType

if TYPE_CHECKING:
    from typing import Any

    from django_spire.ai.chat.message_intel import BaseMessageIntel


@dataclass
class MessageResponse:
    type: MessageResponseType
    sender: str
    message_intel: BaseMessageIntel
    synthesis_speech: bool = False

    def _render_template_to_html_string(self, template: str, context_data: dict[str, Any] | None = None) -> str:
        return render_to_string(
            template_name=template,
            context={
                'sender': self.sender,
                'message_intel': self.message_intel,
                'synthesis_speech': self.synthesis_speech,
                **(context_data or {})
            },
        )

    def render_to_html_string(self, context_data: dict[str, Any] | None = None) -> str:
        if self.type == MessageResponseType.REQUEST:
            return self._render_template_to_html_string(
                'django_spire/ai/chat/message/request_message.html',
                context_data
            )

        if self.type == MessageResponseType.RESPONSE:
            return self._render_template_to_html_string(
                'django_spire/ai/chat/message/response_message.html',
                context_data
            )

        if self.type == MessageResponseType.LOADING_RESPONSE:
            return self._render_template_to_html_string(
                'django_spire/ai/chat/message/loading_response_message.html',
                context_data
            )

        return ''


@dataclass
class MessageResponseGroup:
    message_responses: list[MessageResponse] = field(default_factory=list)

    def add_message_response(self, message_response: MessageResponse) -> None:
        self.message_responses.append(message_response)

    def render_to_html_string(self, context_data: dict[str, Any] | None = None) -> str:
        html_string = ''

        for message_response in self.message_responses:
            html_string += message_response.render_to_html_string(context_data)

        return html_string
