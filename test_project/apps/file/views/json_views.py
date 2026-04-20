from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.contrib.responses.json_response import (
    error_json_response,
    success_json_response,
)
from django_spire.file.exceptions import FileValidationError

from test_project.apps.file import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import JsonResponse


def add_attachment_view(request: WSGIRequest, pk: int) -> JsonResponse:
    if request.method != 'POST':
        return error_json_response('Method not allowed')

    file_example = get_object_or_404(models.FileExample, pk=pk)
    uploaded_file = next(iter(request.FILES.values()), None)

    if uploaded_file is None:
        return error_json_response('No file provided')

    try:
        result = file_example.services.processor.add_attachment(uploaded_file)
    except (FileValidationError, TypeError, ValueError) as e:
        return error_json_response(str(e))

    return success_json_response(file=result.to_dict())


def add_attachments_view(request: WSGIRequest, pk: int) -> JsonResponse:
    if request.method != 'POST':
        return error_json_response('Method not allowed')

    file_example = get_object_or_404(models.FileExample, pk=pk)

    files = []
    for key in request.FILES:
        files.extend(request.FILES.getlist(key))

    if not files:
        return error_json_response('No files provided')

    try:
        result = file_example.services.processor.add_attachments(files)
    except (FileValidationError, TypeError, ValueError) as e:
        return error_json_response(str(e))

    return success_json_response(files=[f.to_dict() for f in result])


def add_validated_attachment_view(request: WSGIRequest, pk: int) -> JsonResponse:
    if request.method != 'POST':
        return error_json_response('Method not allowed')

    file_example = get_object_or_404(models.FileExample, pk=pk)
    uploaded_file = next(iter(request.FILES.values()), None)

    if uploaded_file is None:
        return error_json_response('No file provided')

    try:
        result = file_example.services.processor.add_validated_attachment(uploaded_file)
    except (FileValidationError, TypeError, ValueError) as e:
        return error_json_response(str(e))

    return success_json_response(file=result.to_dict())


def delete_attachment_view(request: WSGIRequest, pk: int, file_pk: int) -> JsonResponse:
    if request.method != 'POST':
        return error_json_response('Method not allowed')

    file_example = get_object_or_404(models.FileExample, pk=pk)
    deleted = file_example.services.processor.delete_attachment(file_pk)

    if not deleted:
        return error_json_response('Attachment not found')

    return success_json_response()


def delete_attachments_view(request: WSGIRequest, pk: int) -> JsonResponse:
    if request.method != 'POST':
        return error_json_response('Method not allowed')

    file_example = get_object_or_404(models.FileExample, pk=pk)
    count = file_example.services.processor.delete_attachments()

    return success_json_response(deleted_count=count)


def delete_profile_picture_view(request: WSGIRequest, pk: int) -> JsonResponse:
    if request.method != 'POST':
        return error_json_response('Method not allowed')

    file_example = get_object_or_404(models.FileExample, pk=pk)
    count = file_example.services.processor.delete_profile_picture()

    return success_json_response(deleted_count=count)


def replace_attachments_view(request: WSGIRequest, pk: int) -> JsonResponse:
    if request.method != 'POST':
        return error_json_response('Method not allowed')

    file_example = get_object_or_404(models.FileExample, pk=pk)

    files = []
    for key in request.FILES:
        files.extend(request.FILES.getlist(key))

    if not files:
        return error_json_response('No files provided')

    try:
        result = file_example.services.processor.replace_attachments(files)
    except (FileValidationError, TypeError, ValueError) as e:
        return error_json_response(str(e))

    return success_json_response(files=[f.to_dict() for f in result])


def replace_profile_picture_view(request: WSGIRequest, pk: int) -> JsonResponse:
    if request.method != 'POST':
        return error_json_response('Method not allowed')

    file_example = get_object_or_404(models.FileExample, pk=pk)
    uploaded_file = next(iter(request.FILES.values()), None)

    if uploaded_file is None:
        return error_json_response('No file provided')

    try:
        result = file_example.services.processor.replace_profile_picture(uploaded_file)
    except (FileValidationError, TypeError, ValueError) as e:
        return error_json_response(str(e))

    return success_json_response(
        file=result.to_dict() if result else None,
    )
