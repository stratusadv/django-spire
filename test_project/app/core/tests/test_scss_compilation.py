import subprocess
import sys
from pathlib import Path

import pytest
from django.conf import settings

from django_spire.core.tests.test_cases import BaseTestCase


@pytest.mark.django_db
class TestSCSSCompilation(BaseTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.scss_source_dir = Path(settings.STATICFILES_DIRS[0]) / 'django_spire' / 'scss'
        self.output_dir = Path(settings.STATICFILES_DIRS[0]) / 'django_spire' / 'css'
        self.output_css_file = self.output_dir / 'django-spire-bootstrap.css'

    def test_compile_scss_uses_external_theme_when_present(self):
        external_theme = self.scss_source_dir / '_theme.scss'
        assert external_theme.exists(), 'External _theme.scss should exist for testing'

        python_exe = Path(sys.executable).resolve()
        result = subprocess.run(
            [str(python_exe), 'manage.py', 'spire_compile_scss'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            env={**subprocess.os.environ, 'DJANGO_SETTINGS_MODULE': 'test_project.test_settings'},
        )

        assert result.returncode == 0, f'SCSS compilation failed: {result.stderr}'
        assert 'Compiled successfully:' in result.stdout

    def test_compile_scss_includes_external_test_utilities(self):
        python_exe = Path(sys.executable).resolve()
        result = subprocess.run(
            [str(python_exe), 'manage.py', 'spire_compile_scss'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            env={**subprocess.os.environ, 'DJANGO_SETTINGS_MODULE': 'test_project.test_settings'},
        )

        assert result.returncode == 0, f'SCSS compilation failed: {result.stderr}'
        assert self.output_css_file.exists(), 'Output CSS file should exist'

        css_content = self.output_css_file.read_text(encoding='utf-8')

        assert '.test-compilation-verification' in css_content
        assert '.test-class-from-external' in css_content
        assert '.test-selector' in css_content

    def test_compile_scss_output_contains_expected_test_values(self):
        python_exe = Path(sys.executable).resolve()
        result = subprocess.run(
            [str(python_exe), 'manage.py', 'spire_compile_scss'],
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR,
            env={**subprocess.os.environ, 'DJANGO_SETTINGS_MODULE': 'test_project.test_settings'},
        )

        assert result.returncode == 0, f'SCSS compilation failed: {result.stderr}'
        css_content = self.output_css_file.read_text(encoding='utf-8')

        assert '#ff0000' in css_content or 'rgb(255, 0, 0)' in css_content.lower()
        assert '#00ff00' in css_content or 'rgb(0, 255, 0)' in css_content.lower()
