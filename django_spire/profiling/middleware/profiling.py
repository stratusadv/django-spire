from __future__ import annotations

import os
import threading
import time

from pathlib import Path
from typing_extensions import Any, Callable, TYPE_CHECKING

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

try:
    from pyinstrument import Profiler
except ImportError:
    Profiler = None

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


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
    '/docs/',
    '/favicon.ico',
    '/media/',
    '/openapi/',
    '/redoc/',
    '/robots.txt',
    '/schema/',
    '/sitemap.xml',
    '/static/',
    '/swagger/',
    'django_glue',
]


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


class ProfilingMiddleware(MiddlewareMixin):
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        super().__init__(get_response)

        if Profiler is None:
            message = 'pyinstrument is required for profiling.'
            raise ImportError(message)

        configuration = {
            'PROFILING_DIR': os.getenv('PROFILING_DIR', '.profile'),
            'PROFILING_ENABLED': os.getenv('PROFILING_ENABLED', 'False') == 'True',
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
        self.profile_threshold = configuration.get('PROFILE_THRESHOLD', 0)

        self.count = 0
        self.lock = threading.Lock()

    def _remove_profile(self) -> None:
        files = self.directory.glob('*.html')
        profiles = list(files)

        profiles.sort(
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        maximum = 10

        if len(profiles) > maximum:
            for profile in profiles[maximum:]:
                profile.unlink()

    def _save_profile(
        self,
        profiler: Profiler,
        request: HttpRequest,
        duration_ms: float
    ) -> None:
        with self.lock:
            timestamp = int(time.time() * 1000)
            method = request.method
            path = request.path.replace('/', '_').replace('.', '_')

            if not path or path == '_':
                path = 'root'

            filename = f'{timestamp}_{method}_{path}_{duration_ms:.1f}ms_{request._profiling_id}.html'

            path = str(self.directory / filename)
            profiler.write_html(path)

            self._remove_profile()

    def _should_skip_profiling(self, request: HttpRequest) -> bool:
        path = request.path

        return (
            any(path.startswith(pattern) or pattern in path for pattern in IGNORE_PATH) or
            any(path.endswith(extension) or extension in path for extension in IGNORE_EXTENSION)
        )

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

        if self._should_skip_profiling(request):
            return None

        with self.lock:
            self.count = self.count + 1
            request._profiling_id = self.count

        profiler = Profiler(interval=0.001)
        start_time = time.time()
        profiler.start()

        try:
            response = view_func(request, *args, **kwargs)

            if hasattr(response, 'render'):
                response.render()
        except Exception:
            profiler.stop()
            duration_ms = (time.time() - start_time) * 1000
            self._save_profile(profiler, request, duration_ms)

            raise
        else:
            profiler.stop()
            duration_ms = (time.time() - start_time) * 1000

            if duration_ms >= self.profile_threshold:
                self._save_profile(profiler, request, duration_ms)

            return response
