from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.http import JsonResponse

from django_spire.core.shortcuts import get_object_or_null_obj
from testing.dummy import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def home(_request: WSGIRequest) -> TemplateResponse:
    dummy = get_object_or_null_obj(models.DummyModel, pk=0)

    data = {'dummy': dummy}
    return JsonResponse(data)
