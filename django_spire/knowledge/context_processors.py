from typing import Any

from django.core.handlers.wsgi import WSGIRequest

from django_spire.knowledge.collection.models import Collection


def django_spire_knowledge(request: WSGIRequest) -> dict[str, Any]:
    if not request.user.is_authenticated:
        return {}

    return {
        'collection_tree_json': Collection.services.transformation.to_hierarchy_json(
            request=request,
        )
    }
