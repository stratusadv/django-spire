from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING

from django_spire.contrib.sync.database.graph import DependencyGraph

if TYPE_CHECKING:
    from django_spire.contrib.sync.django.mixin import SyncableMixin


def build_graph(models: list[type[SyncableMixin]]) -> DependencyGraph:
    labels = {model._meta.label for model in models}
    edges: dict[str, set[str]] = {}

    for model in models:
        label = model._meta.label
        dependencies: set[str] = set()

        for field in chain(model._meta.concrete_fields, model._meta.many_to_many):
            if not field.is_relation:
                continue

            if field.related_model is None:
                continue

            if hasattr(field, 'null') and field.null:
                continue

            target = field.related_model._meta.label

            if target in labels and target != label:
                dependencies.add(target)

        edges[label] = dependencies

    return DependencyGraph(edges)
