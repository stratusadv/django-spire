from typing import Self

from django_spire.metric.report.report import BaseReport


class ReportRegistry:
    category: str | None = None
    report_names_classes: dict[str, BaseReport] = {}
    report_registries: list[Self] = []

    def __init__(self):
        for report_registry in self.report_registries:
            self.add_registry(report_registry)

    def add_registry(
            self,
            report_registry: Self
    ):
        if report_registry.category is None:
            message = 'Report Registry category is required'
            raise ValueError(message)

        # if report_registry.category in self.report_names_classes:
        #     message = f'Report Registry category "{report_registry.category}" already exists'
        #     raise ValueError(message)

        self.report_names_classes[report_registry.category] = report_registry.report_names_classes

    def get_report_from_key_stack(self, report_key_stack: str) -> BaseReport | None:
        current = self.report_names_classes

        for key in report_key_stack.split('|'):
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current()
