from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING

from django_spire.contrib.sync.core.graph import DependencyGraph

if TYPE_CHECKING:
    from django_spire.contrib.sync.django.mixin import SyncableMixin


def build_graph(models: list[type[SyncableMixin]]) -> DependencyGraph:
    labels = {model._meta.label for model in models}

    edges: dict[str, set[str]] = {}

    for model in models:
        dependencies: set[str] = set()

        foreign_keys = chain(
            model._meta.concrete_fields,
            model._meta.many_to_many,
        )

        for field in foreign_keys:
            if not field.is_relation:
                continue

            related_label = field.related_model._meta.label

            if related_label in labels and related_label != model._meta.label:
                if not getattr(field, 'null', True):
                    dependencies.add(related_label)

        edges[model._meta.label] = dependencies

    return DependencyGraph(edges)
