from __future__ import annotations

from django.db.models import Count, QuerySet


class ReportRunQuerySet(QuerySet):
    def by_popular(self) -> QuerySet:
        return (
            self.values('report_key_stack')
            .annotate(run_count=Count('report_key_stack'))
            .order_by('-run_count')
        )

    def by_top_ten(self) -> list[dict]:
        return list(self.by_popular()[:10])

    def run_count(self, report_key_stack: str) -> int:
        return self.filter(report_key_stack=report_key_stack).count()
