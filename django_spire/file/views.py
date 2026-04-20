from __future__ import annotations

import re

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required

from django_spire.contrib.responses.json_response import (
    error_json_response,
    success_json_response,
)
from django_spire.file.exceptions import FileValidationError
from django_spire.file.factory import FileFactory, RELATED_FIELD_LENGTH_MAX

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import JsonResponse


_RELATED_FIELD_PATTERN = re.compile(r'^[a-zA-Z0-9_]*$')


def _validate_related_field(value: str) -> str | None:
    if len(value) > RELATED_FIELD_LENGTH_MAX:
        return f'related_field must not exceed {RELATED_FIELD_LENGTH_MAX} characters.'

    if not _RELATED_FIELD_PATTERN.match(value):
        return 'related_field contains invalid characters.'

    return None


@login_required()
def file_upload_ajax_multiple(request: WSGIRequest) -> JsonResponse:
    if request.method != 'POST':
        return error_json_response('Method not allowed')

    related_field = request.POST.get('related_field', '')
    error = _validate_related_field(related_field)

    if error:
        return error_json_response(error)

    try:
        factory = FileFactory(related_field=related_field)
        files = factory.create_many(list(request.FILES.values()))
    except (FileValidationError, TypeError, ValueError) as e:
        return error_json_response(str(e))

    return success_json_response(files=[file.to_dict() for file in files])


@login_required()
def file_upload_ajax_single(request: WSGIRequest) -> JsonResponse:
    if request.method != 'POST':
        return error_json_response('Method not allowed')

    related_field = request.POST.get('related_field', '')
    error = _validate_related_field(related_field)

    if error:
        return error_json_response(error)

    try:
        uploaded_file = next(iter(request.FILES.values()))
    except StopIteration:
        return error_json_response('No file provided')

    try:
        factory = FileFactory(related_field=related_field)
        file = factory.create(uploaded_file)
    except (FileValidationError, TypeError, ValueError) as e:
        return error_json_response(str(e))

    return success_json_response(file=file.to_dict())
