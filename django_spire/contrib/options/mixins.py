from __future__ import annotations

from django.db import models
from django_spire.contrib.options.options import Options

DEFAULT_OPTIONS = Options(sections=[])


class OptionsModelMixin(models.Model):
    _options = models.JSONField(default=dict)
    _default_options = DEFAULT_OPTIONS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = Options.load_dict(self._options)

    def _sync_options(self):
        if self.options != self._default_options:
            self.options.sync_options(self._default_options)
            self._options = self.options.to_dict()

    def get_option(self, section_name: str, option_key: str):
        self._sync_options()
        return self.options.get_setting(section_name, option_key)

    def update_session(self, request):
        request.session['user_options'] = self.options.to_dict()

    def update_option(
        self,
        section_name: str,
        option_key: str,
        value: str | bool | int,
        commit: bool = True
    ):
        self._sync_options()
        self.options.update_setting(section_name, option_key, value)
        self._options = self.options.to_dict()

        if commit:
            self.save()

    class Meta:
        abstract = True
