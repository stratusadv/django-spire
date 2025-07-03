from django_spire.core.filtering.querysets import FilterQuerySet, SearchQuerySet
from django_spire.core.filtering.session import QuerySetFilterSession


class QuerySetFilter:
    def __init__(
            self,
            request,
            filter_key: str,
            default_filtering_data: dict = None
    ):
        self.request = request
        self.filter_key = filter_key

        # What are the different types for?
        # Searching and Filtering and Clear?
        # If there is a search key then it should automatically search?
        self.user_command = self.request.GET.get('filter_type')

        # This allows us to have multiple filters on the page
        self.user_key = self.request.GET.get('filter_key')

        self.session_helper = QuerySetFilterSession(self.request, self.filter_key)

        if not self.request.GET.get('page') and self.user_command not in ['filter', 'search']:
            self.session_helper.clear()

        if self.user_command == 'clear':
            self.session_helper.clear()
            self.filter_data = default_filtering_data
        elif self.request.GET and self.filter_key == self.user_key:
            self.filter_data = self.request.GET
        elif self.session_helper.has_data():
            self.filter_data = self.session_helper.session_filter_data
        else:
            self.filter_data = (
                default_filtering_data if default_filtering_data is not None else {}
            )

        self.remove_old_data()

        if self.user_command in ['filter', 'search'] or self.request.GET.get('page'):
            self.session_helper.add(self.filter_data.copy())

        self._process_commands()

    def _filter_data_contains_filter_by_keys(self) -> bool:
        return (
            self.filter_data and
            any(
                key not in [
                    'search_value', 'csrfmiddlewaretoken', 'filter_key', 'filter_type'
                ]
                for key in self.filter_data
            )
        )

    def _process_commands(self):
        if self.filter_key == self.user_key and self.user_command == 'clear':
            self.session_helper.clear()

    def remove_old_data(self):
        self.session_helper.clean()

    def process_queryset(
            self,
            queryset: SearchQuerySet | FilterQuerySet,
            ignore_search_query: bool = False
    ):
        if self.filter_data.get('search_value') and not ignore_search_query:
            queryset = queryset.search(self.filter_data.get('search_value'))

        if self._filter_data_contains_filter_by_keys():
            queryset = queryset.filter_by_query_dict(self.filter_data)

        return queryset

    def to_context_data(self) -> dict:
        # Todo: This can be turned into attributes that are accessed from the queryset filter
        return {
            self.filter_key: {
                'has_data': self.session_helper.has_data(),
                'key': self.filter_key
            }
        }
