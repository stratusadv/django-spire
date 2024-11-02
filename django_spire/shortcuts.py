import json

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model


def get_object_or_null_obj(model, pk: int, **kwargs):
    try:
        return model.objects.get(pk=pk, **kwargs)
    except model.DoesNotExist:
        return model()


def get_object_or_none(model, pk, **kwargs):
    try:
        return model.objects.get(pk=pk, **kwargs)
    except model.DoesNotExist:
        return None


def process_request_body(request):
    body_unicode = request.body.decode('utf-8')
    return json.loads(body_unicode)['data']


def model_object_from_app_label(app_label, model_name, object_pk) -> Model | None:
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    except ContentType.DoesNotExist:
        return None

    model_class = content_type.model_class()

    return get_object_or_none(model_class, pk=object_pk)
