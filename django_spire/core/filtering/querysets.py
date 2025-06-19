from abc import abstractmethod

from django.db.models import QuerySet


class FilteringQuerySetMixin(QuerySet):

    @abstractmethod
    def search(self, search_value) -> QuerySet:
        raise NotImplementedError('Must implement search method on queryset.')

    @abstractmethod
    def filter_by_query_dict(self, filter_data: dict) -> QuerySet:
        raise NotImplementedError('Must implement filter_by method on queryset.')
