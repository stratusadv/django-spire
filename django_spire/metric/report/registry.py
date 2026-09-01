from __future__ import annotations

from typing import TYPE_CHECKING, Self

from django_spire.metric.report.report import BaseReport

if TYPE_CHECKING:
    from typing import Any


class ReportRegistry:
    category: str | None = None
    report_names_classes: dict[str, Any] = {}
    report_registries: list[type[Self]] = []

    def __init__(self) -> None:
        self.report_names_classes = {}
        self.report_registries = []

    @classmethod
    def _collect_report_names(cls, registry_class: type[Self]) -> dict[str, Any]:
        report_names = dict(registry_class.report_names_classes)

        for nested_registry in registry_class.report_registries:
            if nested_registry.category is None:
                message = 'Report Registry category is required'
                raise ValueError(message)

            report_names[nested_registry.category] = cls._collect_report_names(nested_registry)

        return report_names

    def add_registry(self, report_registry: type[Self] | Self) -> None:
        registry_class = (
            report_registry if isinstance(report_registry, type) else type(report_registry)
        )

        if registry_class.category is None:
            message = 'Report Registry category is required'
            raise ValueError(message)

        self.report_names_classes[registry_class.category] = self._collect_report_names(
            registry_class
        )

    def get_report_from_key_stack(self, report_key_stack: str) -> BaseReport | None:
        current: Any = self.report_names_classes

        for key in report_key_stack.split('|'):
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        if isinstance(current, dict):
            return None

        if not isinstance(current, type) or not issubclass(current, BaseReport):
            return None

        return current()
