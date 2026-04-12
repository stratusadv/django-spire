from __future__ import annotations

from django.db import models

from django_spire.api.tools import hash_string
from django_spire.history.querysets import HistoryQuerySet


class CeleryTaskQuerySet(HistoryQuerySet):
    pass

