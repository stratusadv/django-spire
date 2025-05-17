import json

from django.http import HttpResponse
from django.conf import settings

from django_spire.ai.chat.responses import MessageResponseGroup, MessageResponse, MessageResponseType
from django_spire.ai.chat.models import Chat
from django_spire.ai.chat.tools import chat_workflow_process
from django_spire.consts import AI_CHAT_WORKFLOW_SETTINGS_NAME


def load_messages_render_view(request, chat_id):
    chat = (
        Chat.objects
        .by_user(request.user)
        .get(id=chat_id)
    )

    message_group = MessageResponseGroup()

    for chat_message in chat.message_responses.all():
        message_group.add_message_response(
            chat_message.to_message(request)
        )

    return HttpResponse(
        message_group.render_to_html_string(
            {
                'chat_id': chat.id,
            }
        )
    )


def request_message_render_view(request):
    body_data = json.loads(request.body)

    chat = (
        Chat.objects
        .by_user(request.user)
        .get(id=body_data['chat_id'])
    )

    if chat.is_empty:
        chat.name = body_data['message_body']
        chat.save()

    message_group = MessageResponseGroup()

    user_message = MessageResponse(
        request=request,
        type=MessageResponseType.REQUEST,
        sender='You',
        body=body_data['message_body']
    )

    message_group.add_message_response(
        user_message
    )

    chat.add_message_response(user_message)

    message_group.add_message_response(
        MessageResponse(
            request=request,
            type=MessageResponseType.LOADING_RESPONSE,
            sender='Spire',
            body=body_data['message_body']
        )
    )

    return HttpResponse(
        message_group.render_to_html_string(
            {
                "chat_id": chat.id,
                "chat_workflow_name": getattr(settings, AI_CHAT_WORKFLOW_SETTINGS_NAME),
            }
        )
    )


def response_message_render_view(request):
    body_data = json.loads(request.body)

    chat = Chat.objects.by_user(request.user).get(id=body_data['chat_id'])

    response = chat_workflow_process(
        request,
        body_data["message_body"],
        message_history=chat.generate_message_history(),
    )

    chat_workflow_name = getattr(settings, AI_CHAT_WORKFLOW_SETTINGS_NAME)

    if chat_workflow_name is None:
        raise ValueError(
            f'"{AI_CHAT_WORKFLOW_SETTINGS_NAME}" must be set in the django settings.'
        )

    llm_message = MessageResponse(
        request=request,
        type=MessageResponseType.RESPONSE,
        sender=chat_workflow_name,
        body=response['text'],
    )

    chat.add_message_response(llm_message)

    return HttpResponse(llm_message.render_to_html_string({'chat_id': chat.id}))
