from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.apps import FileConfig


class FileConfigTests(BaseTestCase):
    def test_default_auto_field(self) -> None:
        assert FileConfig.default_auto_field == 'django.db.models.BigAutoField'

    def test_label(self) -> None:
        assert FileConfig.label == 'django_spire_file'

    def test_name(self) -> None:
        assert FileConfig.name == 'django_spire.file'

    def test_required_apps(self) -> None:
        assert FileConfig.REQUIRED_APPS == ('django_spire_core',)

    def test_urlpatterns_include(self) -> None:
        assert FileConfig.URLPATTERNS_INCLUDE == 'django_spire.file.urls'

    def test_urlpatterns_namespace(self) -> None:
        assert FileConfig.URLPATTERNS_NAMESPACE == 'file'
