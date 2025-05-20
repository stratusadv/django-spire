from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import messages

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def show_form_errors(request: WSGIRequest, *forms) -> None:
    for form in forms:
        for field_name, error_list in form.errors.items():
            for error in error_list.data:
                error_message = f'{field_name.title()}: {" ".join(error.message_responses)}'
                messages.error(request, error_message)
