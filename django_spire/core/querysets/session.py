from datetime import datetime, timedelta

from django.core.handlers.wsgi import WSGIRequest


class QuerySetFilterSession:

    def __init__(
            self,
            request: WSGIRequest,
            filter_key: str,
            timeout: int = 60 * 5
    ):
        self.request = request
        self.filter_key = filter_key
        self.timeout = timeout

        self.base_key = 'django_spire_queryset_filter_session'

        if self.session_key not in self.request.session:
            self.request.session[self.session_key] = {}

        self.data = self.request.session[self.session_key]

        self._clean()
        self._check_for_updates()

    def _check_for_updates(self):
        # Todo: Setup adding and clearing data.
        # Looks at the request GET data and updates it according.
        # Clears the data if needed.
        # Must have a session key
        pass

    def _clean(self) -> None:
        if self.has_data:
            current_timestamp = datetime.now().timestamp()
            timeout = self.data.get('_timeout', 0)

            if timeout < current_timestamp:
                self._clear()

    def _clear(self) -> None:
        del self.request.session[self.session_key][self.filter_key]
        self.request.session.modified = True

    def _set_modified(self):
        self.request.session.modified = True

    @property
    def has_data(self) -> bool:
        return bool(self.data)

    @property
    def session_key(self):
        return f'{self.base_key}_{self.filter_key}'

    def add(self, data: dict):
        data['_timeout'] = (datetime.now() + timedelta(seconds=self.timeout)).timestamp()
        data.pop('csrfmiddlewaretoken', None)
        data.pop('filter_type', None)
        data.pop('filter_key', None)
        self.request.session[self._session_key][self.filter_key] = data
        self.request.session.modified = True
