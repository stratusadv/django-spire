from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest


class BaseSession:
    json_serializable: bool = False
    session_key: str | None = None


    def __init__(
            self,
            request: HttpRequest,
            seconds_till_expiry: int = 60 * 5
    ):
        self.request = request
        self.seconds_till_expiry = seconds_till_expiry

        self.request.session.setdefault(self.session_key, dict())
        self._session = self.request.session[self.session_key]

        # self._clean()

    def __getitem__(self, key: str) -> Any:
        return self._session[key]

    def __setitem__(self, key: str, value: Any):
        self.add_data(key, value)

    def add_data(self, key: str, data: Any):
        self._session[key] = data
        self._set_timeout_datestamp()
        self._set_modified()

    @property
    def data(self):
        return self._session

    @property
    def is_expired(self) -> bool:
        current_timestamp = datetime.now().timestamp()
        timeout = self.data.get('_timeout_datestamp', 0)
        return timeout < current_timestamp

    def remove_data(self, key: str):
        self._session.pop(key)
        self._set_modified()

        # remove the session completely if there is no data in it.
        if '_timeout_datestamp' in self._session and len(self._session.keys()) == 1:
            self._session.pop('_timeout_datestamp')

    def _clean(self) -> None:
        """
            This will purge the current session.
            What happens if this session does not get called? It will sit there.
            Should it purge all sessions?
        """

        if self.is_expired:
            self.request.session.pop(self.session_key)
            self._set_modified()

    def _set_modified(self):
        self.request.session.modified = True

    @property
    def has_data(self) -> bool:
        return bool(self._session)

    def _set_timeout_datestamp(self):
        timeout_datetime = datetime.now() + timedelta(seconds=self.seconds_till_expiry)
        self._session['_timeout_datestamp'] = timeout_datetime.timestamp()

    def to_json(self):
        if not self.json_serializable:
            raise ValueError(f'Session {self._session.__class__.__name__} is not JSON serializable. ')

        return json.dumps(self._session, cls=DjangoJSONEncoder)