from __future__ import annotations

from django.db.models import Count, F, FloatField, Q, QuerySet, Value
from django.db.models.functions import Cast

from django_spire.contrib.queryset.filter_tools import filter_by_lookup_map
from django_spire.contrib.queryset.mixins import SearchQuerySetMixin, SessionFilterQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet


class TaskQuerySet(
    HistoryQuerySet,
    SessionFilterQuerySetMixin,
    SearchQuerySetMixin,
):
    def annotate_calculated_cost(self) -> QuerySet:
        return self.annotate(
            calculated_cost=Cast(F('id') * Value(100), FloatField())
        )

    def annotate_calculated_price(self) -> QuerySet:
        return self.annotate(
            calculated_price=Cast(F('id') * Value(150), FloatField())
        )

    def annotate_user_count(self) -> QuerySet:
        return self.annotate(
            user_count=Count('user')
        )

    def bulk_filter(self, filter_data: dict) -> QuerySet[TaskQuerySet]:
        queryset = self

        filter_map = {
            'name': 'name__icontains',
            'status': 'status',
            'users': 'user__user__id__in'
        }

        search_term = filter_data.get('search')
        if search_term:
            queryset = queryset.search(search_term)

        return filter_by_lookup_map(queryset, filter_map, filter_data)

    def complete(self) -> QuerySet:
        return self.filter(is_complete=True)

    def prefetch_users(self) -> QuerySet:
        return self.prefetch_related('users__user')

    def search(self, search_value: str | None) -> QuerySet:
        if not search_value:
            return self

        search_value = search_value.strip()

        return self.filter(
            Q(name__icontains=search_value) |
            Q(description__icontains=search_value)
        )

    def sort_by_column(self, sort_column: str, sort_direction: str = 'asc') -> QuerySet:
        sort_mapping = {
            'name': 'name',
            'status': 'status',
            'quantity': 'user_count',
            'cost': 'calculated_cost',
            'date': 'created_datetime',
        }

        sort_field = sort_mapping.get(sort_column, 'created_datetime')
        order_by = f"{'-' if sort_direction == 'desc' else ''}{sort_field}"

        return self.order_by(order_by)


class TaskUserQuerySet(QuerySet):
    def annotate_calculated_cost(self) -> QuerySet:
        return self.annotate(
            calculated_cost=Cast(Value(50) + F('task_id'), FloatField())
        )

    def annotate_calculated_price(self) -> QuerySet:
        return self.annotate(
            calculated_price=Cast(Value(75) + F('task_id'), FloatField())
        )

    def annotate_user_cost(self) -> QuerySet:
        return self.annotate(
            calculated_cost=Cast(F('task__id') * Value(100), FloatField())
        )
