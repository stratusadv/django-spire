from abc import abstractmethod

from django.db.models import QuerySet


class FilterQuerySet(QuerySet):
    @abstractmethod
    def filter_by_query_dict(self, filter_data: dict) -> QuerySet:
        raise NotImplementedError('Must implement filter_by method on queryset.')


class SearchQuerySet(QuerySet):
    @abstractmethod
    def search(self, search_value: str) -> QuerySet:
        raise NotImplementedError('Must implement search method on queryset.')
