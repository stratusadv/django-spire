from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django_spire.file.interfaces import MultiFileUploader, SingleFileUploader


@login_required
def file_multiple_upload_ajax(request):
    if request.method == 'POST':
        file_uploader = MultiFileUploader(request.POST.get('related_field', ''))
        files = file_uploader.upload(list(request.FILES.values()))
        return JsonResponse({
            'files': [file.to_dict() for file in files]
        })


@login_required
def file_single_upload_ajax(request):
    if request.method == 'POST':
        file_uploader = SingleFileUploader(request.POST.get('related_field', ''))
        file = file_uploader.upload(list(request.FILES.values())[0])
        return JsonResponse({
            'file': file.to_dict()
        })
