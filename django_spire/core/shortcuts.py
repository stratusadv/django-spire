from __future__ import annotations

import json

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from typing_extensions import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest
    from typing_extensions import Any


T = TypeVar('T', bound=Model)


def get_object_or_null_obj(queryset_or_model: QuerySet[T] | type[T], **kwargs) -> T:
    if not hasattr(queryset_or_model, 'get'):
        queryset = queryset_or_model._default_manager.all()
    else:
        queryset = queryset_or_model

    try:
        return queryset.get(**kwargs)
    except queryset.model.DoesNotExist:
        return queryset.model()


def get_object_or_none(model: type[Model], pk: int, **kwargs) -> Model:
    try:
        return model.objects.get(pk=pk, **kwargs)
    except model.DoesNotExist:
        return None


def process_request_body(request: HttpRequest) -> Any:
    body_unicode = request.body.decode('utf-8')
    return json.loads(body_unicode)['data']


def model_object_from_app_label(
    app_label: str,
    model_name: str,
    object_pk: int
) -> Model | None:
    try:
        content_type = ContentType.objects.get(
            app_label=app_label,
            model=model_name
        )
    except ContentType.DoesNotExist:
        return None

    model_class = content_type.model_class()
    return get_object_or_none(model_class, pk=object_pk)
