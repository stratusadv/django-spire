from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.forms import Form


def form_errors_as_list(form: Form) -> list[str]:
    form_errors = []
    for field_name, error_list in form.errors.items():
        for error in error_list.data:
            error_message = ''

            if field_name != '__all__':
                error_message += f'{field_name.title()}: '

            if hasattr(error, 'message_responses'):
                error_message += f'{" ".join(error.message_responses)}'

            elif hasattr(error, 'messages'):
                error_message += f'{" ".join(error.messages)}'

            else:
                raise Exception('Error message not found.')

            form_errors.append(error_message)

    return form_errors


def show_form_errors(request: WSGIRequest, *forms: Form) -> None:
    for form in forms:
        for error in form_errors_as_list(form):
            messages.error(request=request, message=error)
