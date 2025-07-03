from django.db.models import QuerySet, Q

from django_spire.core.filtering.querysets import FilterQuerySet, SearchQuerySet


class TaskQuerySet(
    FilterQuerySet,
    SearchQuerySet
):

    def active(self) -> QuerySet:
        return self.filter(is_active=True, is_deleted=False)

    def complete(self) -> QuerySet:
        return self.filter(is_complete=True)

    def filter_by_query_dict(self, filter_data: dict) -> QuerySet:
        query = Q()

        age = filter_data.get('age')
        if age:
            query &= Q(age=age)

        return self.filter(query)

    def search(self, search_query: str) -> QuerySet:
        return self.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )