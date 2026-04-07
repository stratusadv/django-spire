from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from test_project.apps.rest.services.rest.service import TestRestUserRestService

if TYPE_CHECKING:
    from test_project.apps.rest.models import TestRestUser


class TestRestUserService(BaseDjangoModelService['TestRestUser']):
    obj: TestRestUser
    rest = TestRestUserRestService()
