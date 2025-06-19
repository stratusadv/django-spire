from abc import ABC
from datetime import datetime, timedelta


class QuerySetFilterSession(ABC):
    _session_key: str = 'list_filter'

    def __init__(self, request, filter_key: str, timeout: int = 60 * 5):
        self.request = request
        self.filter_key = filter_key
        self.timeout = timeout

        if self._session_key not in self.request.session:
            self.request.session[self._session_key] = {}

    @property
    def session_filter_data(self) -> dict:
        return self.request.session[self._session_key].get(self.filter_key, {})

    def add(self, data: dict):
        data['_timeout'] = (datetime.now() + timedelta(seconds=self.timeout)).timestamp()
        data.pop('csrfmiddlewaretoken', None)
        data.pop('filter_type', None)
        data.pop('filter_key', None)
        self.request.session[self._session_key][self.filter_key] = data
        self.request.session.modified = True

    def has_data(self) -> bool:
        return bool(self.session_filter_data)

    def clean(self) -> None:
        if self.has_data():
            current_timestamp = datetime.now().timestamp()
            timeout = self.session_filter_data.get('_timeout', 0)

            if timeout < current_timestamp:
                self.clear()

    def clear(self) -> None:
        if self.has_data():
            del self.request.session[self._session_key][self.filter_key]
            self.request.session.modified = True
