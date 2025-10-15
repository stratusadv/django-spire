from __future__ import annotations

import os
import threading
import time

from pathlib import Path
from typing_extensions import TYPE_CHECKING

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from django_spire.profiling import lock

try:
    from pyinstrument import Profiler
except ImportError:
    Profiler = None

if TYPE_CHECKING:
    from typing_extensions import Any, Callable

    from django.http import HttpRequest, HttpResponse


IGNORE_EXTENSION = [
    '.eot',
    '.gif',
    '.ico',
    '.jpeg',
    '.jpg',
    '.js',
    '.map',
    '.pdf',
    '.png',
    '.svg',
    '.ttf',
    '.txt',
    '.woff',
    '.woff2',
    '.zip',
]

IGNORE_PATH = [
    '/__',
    '/__debug__/',
    '/__debug__/history_sidebar/',
    '/__reload__/events/',
    '/_admin_profiling/',
    '/admin/',
    '/admin/autocomplete/',
    '/admin/jsi18n/',
    '/api-auth/',
    '/api-auth/login/',
    '/api-auth/logout/',
    '/api/schema/',
    '/browsable-api/',
    '/debug/',
    '/debug-toolbar/',
    '/django_glue/',
    '/django_spire/theme/json/get_config/',
    '/docs/',
    '/favicon.ico',
    '/media/',
    '/openapi/',
    '/redoc/',
    '/robots.txt/',
    '/schema/',
    '/sitemap.xml',
    '/static/',
    '/swagger/',
    'django_glue',
]


class ProfilingMiddleware(MiddlewareMixin):
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        super().__init__(get_response)

        configuration = {
            'PROFILING_DIR': os.getenv('PROFILING_DIR', '.profile'),
            'PROFILING_ENABLED': os.getenv('PROFILING_ENABLED', 'False') == 'True',
            'PROFILING_MAX_FILES': int(os.getenv('PROFILING_MAX_FILES', '10')),
            'PROFILE_THRESHOLD': float(os.getenv('PROFILE_THRESHOLD', '0')),
        }

        directory = configuration.get('PROFILING_DIR', '.profile')

        if isinstance(directory, str):
            if not Path(directory).is_absolute():
                current = Path.cwd()
                base = getattr(settings, 'BASE_DIR', current)
                directory = Path(base) / directory
            else:
                directory = Path(directory)

        self.directory = Path(directory)
        self.directory.mkdir(exist_ok=True)

        self.enabled = configuration.get('PROFILING_ENABLED', False)
        self.threshold = configuration.get('PROFILE_THRESHOLD', 0)
        self.maximum = configuration.get('PROFILING_MAX_FILES', 10)

        self.count = 0
        self.lock = threading.Lock()

    def _remove_profiles(self) -> None:
        files = list(self.directory.glob('*.html'))

        if len(files) <= self.maximum:
            return

        files.sort(
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True
        )

        for profile in files[self.maximum:]:
            if profile.exists():
                profile.unlink()

    def _save_profile(self, profiler: Profiler, request: HttpRequest, duration: float) -> None:
        with self.lock:
            timestamp = int(time.time() * 1000)
            method = request.method
            path = request.path.replace('/', '_').replace('.', '_')

            if not path or path == '_':
                path = 'root'

            profileid = request._profiling_id
            filename = f'{timestamp}_{method}_{path}_{duration:.1f}ms_{profileid}.html'
            filepath = self.directory / filename

            with lock:
                profiler.write_html(str(filepath))
                self._remove_profiles()

    def _should_skip(self, request: HttpRequest) -> bool:
        path = request.path

        path_match = any(
            path.startswith(pattern) or pattern in path
            for pattern in IGNORE_PATH
        )

        extension_match = any(
            path.endswith(extension) or extension in path
            for extension in IGNORE_EXTENSION
        )

        return path_match or extension_match

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any]
    ) -> Any:
        if not settings.DEBUG:
            return None

        if not self.enabled:
            return None

        if self._should_skip(request):
            return None

        with self.lock:
            self.count = self.count + 1
            request._profiling_id = self.count

        profiler = Profiler(interval=0.001)
        start = time.time()
        profiler.start()

        try:
            response = view_func(request, *args, **kwargs)

            if hasattr(response, 'render'):
                response.render()
        except Exception:
            profiler.stop()
            duration = (time.time() - start) * 1000
            self._save_profile(profiler, request, duration)

            raise
        else:
            profiler.stop()
            duration = (time.time() - start) * 1000

            if duration >= self.threshold:
                self._save_profile(profiler, request, duration)

            return response
