from pathlib import Path

from django.apps import AppConfig
from django.conf import settings


class DjangoSpireConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_core'
    name = 'django_spire.core'

    URLPATTERNS_INCLUDE = 'django_spire.core.urls'
    URLPATTERNS_NAMESPACE = 'core'

    def ready(self) -> None:
        try:
            import sass
        except ImportError:
            return

        base_dir = Path(__file__).resolve().parent
        scss_dir = base_dir / 'static' / 'django_spire' / 'scss'
        css_dir = base_dir / 'static' / 'django_spire' / 'css'

        if not scss_dir.exists():
            return

        css_dir.mkdir(parents=True, exist_ok=True)

        for scss_file in scss_dir.glob('*.scss'):
            if scss_file.name.startswith('_'):
                continue

            css_file = css_dir / scss_file.name.replace('.scss', '.css')

            if not css_file.exists() or scss_file.stat().st_mtime > css_file.stat().st_mtime:
                with open(scss_file, 'r', encoding='utf-8') as handle:
                    scss_content = handle.read()

                if not scss_content.strip():
                    with open(css_file, 'w', encoding='utf-8') as handle:
                        handle.write('')
                    continue

                css_content = sass.compile(
                    string=scss_content,
                    output_style='compressed',
                    include_paths=[str(scss_dir)]
                )

                with open(css_file, 'w', encoding='utf-8') as handle:
                    handle.write(css_content)

        if settings.DEBUG:
            from django_spire.core.scss_watcher import ScssWatcher
            watcher = ScssWatcher(scss_dir, css_dir)
            watcher.start()
