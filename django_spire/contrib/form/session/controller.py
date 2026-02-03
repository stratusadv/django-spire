import json

from django.forms import Form
from django.http import HttpRequest

from django_spire.contrib.session.controller import SessionController


class FormSessionController(SessionController):
    def __init__(
        self,
        form_class: type[Form],
        request: HttpRequest,
        session_key: str,
        seconds_till_expiry: int = 60 * 5,
        is_from_body: bool = False
    ):
        data = json.loads(request.body.decode('utf-8')) if is_from_body else request.GET

        self.form = form_class(data)

        if self.form.is_valid():
            super().__init__(request, session_key, seconds_till_expiry)

            if session_key == data.get('session_filter_key'):
                for key, value in self.form.cleaned_data.items():
                    self.add_data(key, value)
