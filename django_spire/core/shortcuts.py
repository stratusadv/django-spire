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
    """
    Retrieves an object from the given QuerySet or model using the
    provided keyword arguments.

    If the object does not exist, returns a new instance of the model.

    :param queryset_or_model: A QuerySet or model class to query from.
    :param kwargs: Keyword arguments for filtering the object.
    :return: An instance of the model, either retrieved or a new instance if not found.
    """

    if not hasattr(queryset_or_model, 'get'):
        queryset = queryset_or_model._default_manager.all()
    else:
        queryset = queryset_or_model

    try:
        return queryset.get(**kwargs)
    except queryset.model.DoesNotExist:
        return queryset.model()


def get_object_or_none(model: type[T], pk: int, **kwargs) -> Model:
    """
    Retrieves an object from the given model using its primary key and additional filters.

    :param model: The model class to query.
    :param pk: The primary key of the object.
    :param kwargs: Additional filter parameters.
    :return: The model instance if found, otherwise None.
    """

    try:
        return model.objects.get(pk=pk, **kwargs)
    except model.DoesNotExist:
        return None


def process_request_body(request: HttpRequest) -> Any:
    """
    Processes the HTTP request body and returns the 'data' field from the parsed JSON.

    :param request: The HTTP request object.
    :return: The 'data' field extracted from the JSON body.
    """

    body_unicode = request.body.decode('utf-8')
    return json.loads(body_unicode)['data']


def model_object_from_app_label(
    app_label: str,
    model_name: str,
    object_pk: int
) -> Model | None:
    """
    Retrieves a model instance based on the application label, model name, and primary key.

    :param app_label: The application label of the model.
    :param model_name: The name of the model.
    :param object_pk: The primary key of the object.
    :return: The model instance if found, otherwise None.
    """

    try:
        content_type = ContentType.objects.get(
            app_label=app_label,
            model=model_name
        )
    except ContentType.DoesNotExist:
        return None

    model_class = content_type.model_class()
    return get_object_or_none(model_class, pk=object_pk)
