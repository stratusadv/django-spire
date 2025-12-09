from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django_spire.file.interfaces import MultiFileUploader, SingleFileUploader

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def file_multiple_upload_ajax(request: WSGIRequest) -> JsonResponse:
    if request.method == 'POST':
        file_uploader = MultiFileUploader(request.POST.get('related_field', ''))
        files = file_uploader.upload(list(request.FILES.values()))

        return JsonResponse({
            'files': [file.to_dict() for file in files]
        })

    return None


@login_required()
def file_single_upload_ajax(request: WSGIRequest) -> JsonResponse:
    if request.method == 'POST':
        file_uploader = SingleFileUploader(request.POST.get('related_field', ''))
        file = file_uploader.upload(next(iter(request.FILES.values())))

        return JsonResponse({
            'file': file.to_dict()
        })

    return None
