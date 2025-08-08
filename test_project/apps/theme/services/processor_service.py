from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from test_project.apps.theme.models import Theme


class ThemeProcessorService(BaseDjangoModelService['Theme']):
    obj: Theme
