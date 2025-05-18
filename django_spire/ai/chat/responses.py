from dataclasses import dataclass, field
from typing import List

from django.template.loader import render_to_string

from django_spire.ai.chat.choices import MessageResponseType
from django_spire.ai.chat.messages import BaseMessageIntel


@dataclass
class MessageResponse:
    type: MessageResponseType
    sender: str
    message_intel: BaseMessageIntel

    def _render_template_to_html_string(self, template: str, context_data: dict = None) -> str:
        return render_to_string(
            template_name=template,
            context={
                'message_intel': self.message_intel.model_dump(),
                **(context_data or {})
            },
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
