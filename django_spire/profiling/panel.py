from __future__ import annotations

import os
import time

from datetime import datetime
from pathlib import Path
from typing_extensions import Any

from debug_toolbar.panels import Panel
from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.urls import re_path
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


class ProfilingPanel(Panel):
    nav_title = 'Profiles'
    template = 'panel.html'
    title = 'Profiling'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory = self._get_directory()

    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f'{size:.1f} {unit}'

            size /= 1024.0

        return f'{size:.1f} TB'

    def _get_directory(self) -> Path:
        location = os.getenv('PROFILING_DIR', '.profile')

        if isinstance(location, str):
            if not Path(location).is_absolute():
                current = Path.cwd()
                base = getattr(settings, 'BASE_DIR', current)
                location = Path(base) / location
            else:
                location = Path(location)

        return Path(location)

    def _get_files(self) -> list[dict[str, Any]]:
        profiles = []

        if not self.directory.exists():
            return profiles

        files = sorted(
            self.directory.glob('*.html'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for file in files:
            stat = file.stat()
            parts = file.stem.split('_')

            if len(parts) >= 4:
                timestamp = int(parts[0]) / 1000
                method = parts[1]
                pathpart = '_'.join(parts[2:-2])
                duration = parts[-2] if len(parts) > 3 else 'N/A'
                profileid = parts[-1] if len(parts) > 4 else 'N/A'
            else:
                timestamp = stat.st_mtime
                method = 'UNKNOWN'
                pathpart = file.stem
                duration = 'N/A'
                profileid = 'N/A'

            if pathpart == 'root':
                display = '/'
            else:
                display = pathpart.replace('_', '/')

                if not display.startswith('/'):
                    display = '/' + display

            mst = timezone.get_fixed_timezone(-360)
            modified = datetime.fromtimestamp(timestamp, tz=mst)

            profiles.append({
                'filename': file.name,
                'path': display,
                'method': method,
                'duration': duration,
                'profileid': profileid,
                'size': self._format_size(stat.st_size),
                'modified': modified.strftime('%b %d, %Y %I:%M %p MST'),
                'timestamp': timestamp,
            })

        return profiles

    def generate_stats(self, request: HttpRequest, response: HttpResponse) -> None:
        profiles = self._get_files()

        profiling = os.getenv('PROFILING_ENABLED', 'False') == 'True'

        total = 0

        if self.directory.exists():
            for file in self.directory.glob('*.html'):
                total += file.stat().st_size

        self.record_stats({
            'profiles': profiles,
            'count': len(profiles),
            'directory': str(self.directory),
            'totalsize': self._format_size(total),
            'enabled': profiling,
        })

    @classmethod
    def get_urls(cls) -> list:
        return [
            re_path(r'^profiling/view/(?P<filename>[^/]+)/$', cls.serve_file, name='profiling_view'),
            re_path(r'^profiling/delete/(?P<filename>[^/]+)/$', csrf_exempt(cls.delete_file), name='profiling_delete'),
            re_path(r'^profiling/list/$', cls.list_files, name='profiling_list'),
        ]

    @property
    def nav_subtitle(self) -> str:
        count = len(list(self.directory.glob('*.html'))) if self.directory.exists() else 0
        return f'{count} profiles'

    @classmethod
    def delete_file(cls, request: HttpRequest, filename: str) -> JsonResponse:
        message = 'Invalid filename'

        if '..' in filename or '/' in filename or '\\' in filename:
            return JsonResponse({'error': message}, status=400)

        message = 'Only HTML files are allowed'

        if not filename.endswith('.html'):
            return JsonResponse({'error': message}, status=400)

        location = os.getenv('PROFILING_DIR', '.profile')

        if not Path(location).is_absolute():
            base = getattr(settings, 'BASE_DIR', Path.cwd())
            location = Path(base) / location
        else:
            location = Path(location)

        filepath = location / filename

        if not filepath.exists():
            return JsonResponse({'success': True, 'already_deleted': True})

        if not filepath.is_file():
            return JsonResponse({'error': 'Not a file'}, status=400)

        try:
            filepath.resolve().relative_to(location.resolve())
        except ValueError:
            message = 'Invalid file path'
            return JsonResponse({'error': message}, status=400)

        attempts = 3

        for i in range(attempts):
            try:
                filepath.unlink()
                return JsonResponse({'success': True})
            except FileNotFoundError:
                return JsonResponse({'success': True, 'already_deleted': True})
            except PermissionError:
                if i < attempts - 1:
                    time.sleep(0.1)
                else:
                    return JsonResponse({'error': 'File is in use, try again'}, status=409)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

        return None

    @classmethod
    def list_files(cls, request: HttpRequest) -> JsonResponse:
        location = os.getenv('PROFILING_DIR', '.profile')

        if not Path(location).is_absolute():
            base = getattr(settings, 'BASE_DIR', Path.cwd())
            location = Path(base) / location
        else:
            location = Path(location)

        panel = cls(None, None)
        panel.directory = location
        profiles = panel._get_files()

        total = 0

        if location.exists():
            for file in location.glob('*.html'):
                total += file.stat().st_size

        return JsonResponse({
            'profiles': profiles,
            'count': len(profiles),
            'totalsize': panel._format_size(total),
        })

    @classmethod
    def serve_file(cls, request: HttpRequest, filename: str) -> HttpResponse:
        message = 'Invalid filename'

        if '..' in filename or '/' in filename or '\\' in filename:
            raise Http404(message)

        message = 'Only HTML files are allowed'

        if not filename.endswith('.html'):
            raise Http404(message)

        location = os.getenv('PROFILING_DIR', '.profile')

        if not Path(location).is_absolute():
            base = getattr(settings, 'BASE_DIR', Path.cwd())
            location = Path(base) / location
        else:
            location = Path(location)

        filepath = location / filename

        message = 'File not found'

        if not filepath.exists() or not filepath.is_file():
            raise Http404(message)

        try:
            filepath.resolve().relative_to(location.resolve())
        except ValueError as error:
            message = 'Invalid file path'
            raise Http404(message) from error
        else:
            with open(filepath, 'r', encoding='utf-8') as handle:
                file = handle.read()

            return HttpResponse(file, content_type='text/html')
