from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING

from django_spire.contrib.sync.core.exceptions import CircularDependencyError
from django_spire.contrib.sync.core.graph import DependencyGraph

if TYPE_CHECKING:
    from django_spire.contrib.sync.django.mixin import SyncableMixin


@dataclass(frozen=True)
class DeferredForeignKey:
    source_label: str
    target_label: str
    field_name: str
    attname: str


def _has_cycle(edges: dict[str, set[str]]) -> bool:
    unvisited, in_stack, done = 0, 1, 2
    state: dict[str, int] = dict.fromkeys(edges, unvisited)

    def visit(node: str) -> bool:
        state[node] = in_stack

        for neighbor in edges.get(node, set()):
            neighbor_state = state.get(neighbor, done)

            if neighbor_state == in_stack:
                return True

            if neighbor_state == unvisited and visit(neighbor):
                return True

        state[node] = done
        return False

    return any(
        visit(node)
        for node in edges
        if state[node] == unvisited
    )


def build_graph(
    models: list[type[SyncableMixin]],
) -> DependencyGraph:
    labels = {model._meta.label for model in models}

    required_edges: dict[str, set[str]] = {}
    optional_edges: dict[str, set[str]] = {}

    for model in models:
        required: set[str] = set()
        optional: set[str] = set()

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
                    required.add(related_label)
                else:
                    optional.add(related_label)

        required_edges[model._meta.label] = required
        optional_edges[model._meta.label] = optional

    if _has_cycle(required_edges):
        involved = {
            label
            for label, deps in required_edges.items()
            if deps
        }

        message = (
            f'Non-nullable foreign keys form a circular dependency '
            f'among: {involved}'
        )

        raise CircularDependencyError(message)

    ordering_edges = {
        label: set(deps)
        for label, deps in required_edges.items()
    }

    deferred_edges: dict[str, set[str]] = {
        label: set() for label in ordering_edges
    }

    for source in sorted(optional_edges):
        for target in sorted(optional_edges[source]):
            ordering_edges[source].add(target)

            if _has_cycle(ordering_edges):
                ordering_edges[source].discard(target)
                deferred_edges[source].add(target)

    deferred_edges = {
        label: targets
        for label, targets in deferred_edges.items()
        if targets
    }

    return DependencyGraph(
        ordering_edges,
        deferred_edges=deferred_edges or None,
    )


def get_deferred_fk_columns(
    models: list[type[SyncableMixin]],
    graph: DependencyGraph,
) -> list[DeferredForeignKey]:
    label_to_model = {m._meta.label: m for m in models}
    syncable_labels = set(label_to_model.keys())
    result: list[DeferredForeignKey] = []

    for source_label, targets in graph.deferred_edges.items():
        model = label_to_model[source_label]

        for field in chain(
            model._meta.concrete_fields,
            model._meta.many_to_many,
        ):
            if not field.is_relation:
                continue

            target_label = field.related_model._meta.label

            if target_label in targets:
                result.append(DeferredForeignKey(
                    source_label=source_label,
                    target_label=target_label,
                    field_name=field.name,
                    attname=field.attname,
                ))

    for model in models:
        for field in model._meta.concrete_fields:
            if not field.is_relation:
                continue

            if not getattr(field, 'null', False):
                continue

            target_label = field.related_model._meta.label

            is_self_ref = (
                target_label == model._meta.label
            )

            is_external = (
                target_label not in syncable_labels
            )

            if not is_self_ref and not is_external:
                continue

            result.append(DeferredForeignKey(
                source_label=model._meta.label,
                target_label=target_label,
                field_name=field.name,
                attname=field.attname,
            ))

    return result


def get_fk_columns_for_cascade(
    models: list[type[SyncableMixin]],
) -> dict[str, list[tuple[str, str]]]:
    syncable_labels = {model._meta.label for model in models}
    result: dict[str, list[tuple[str, str]]] = {}

    for model in models:
        columns: list[tuple[str, str]] = []

        for field in model._meta.concrete_fields:
            if not field.is_relation:
                continue

            target_label = field.related_model._meta.label

            if target_label not in syncable_labels:
                continue

            columns.append((field.attname, target_label))

        if columns:
            result[model._meta.label] = columns

    return result
