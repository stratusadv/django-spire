from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import QuerySet, Count

if TYPE_CHECKING:
    pass


class ReportRunQuerySet(QuerySet):
    def by_popular(self):
        return (
            self
            .values('report_key_stack')
            .annotate(
                run_count=Count('report_key_stack')
            )
            .order_by('-run_count')
        )

    def by_top_ten(self):
        return self.by_popular()[:10]

    def run_count(self, report_key_stack: str) -> int:
        return self.filter(report_key_stack=report_key_stack).count()
