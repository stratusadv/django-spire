from __future__ import annotations

from django.http import HttpResponse
from django.urls import reverse


def reverse_generic_relation(content_object, **kwargs):
    from operator import attrgetter

    model_name = content_object.__class__.__name__.lower()

    CONTENT_OBJECT_URL_MAP = {
        # 'APP_NAME': ('URL', ('pk', 'pk')),
    }

    url_path = None

    if isinstance(CONTENT_OBJECT_URL_MAP[model_name], tuple):
        url_path = CONTENT_OBJECT_URL_MAP[model_name][0]
        for kwarg in CONTENT_OBJECT_URL_MAP[model_name][1:]:
            if kwarg[0] == 'pk':
                if isinstance(kwarg[1], str):
                    kwargs[kwarg[0]] = getattr(content_object, kwarg[1])
                elif isinstance(kwarg[1], int):
                    kwargs[kwarg[0]] = kwarg[1]
            elif kwarg[1] == 'parent_pk':
                retriever = attrgetter(kwarg[2])
                kwargs[kwarg[0]] = retriever(content_object)
    elif isinstance(CONTENT_OBJECT_URL_MAP[model_name], str):
        url_path = CONTENT_OBJECT_URL_MAP[model_name]

    if url_path is not None:
        return reverse(url_path, kwargs=kwargs)

    return HttpResponse('home:home')
