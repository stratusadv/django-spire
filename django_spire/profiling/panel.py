from __future__ import annotations

import os
import time

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing_extensions import Any, TYPE_CHECKING

from debug_toolbar.panels import Panel
from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.urls import re_path
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from django_spire.profiling import lock

if TYPE_CHECKING:
    from typing_extensions import Any


@dataclass
class Profile:
    filename: str
    path: str
    method: str
    duration: str
    profile_id: str
    size: str
    modified: str
    timestamp: float


@dataclass
class ProfileStats:
    profiles: list[Profile]
    count: int
    directory: str
    total_size: str
    enabled: bool


@dataclass
class ProfileList:
    profiles: list[dict[str, Any]]
    count: int
    total_size: str


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

    def _get_files(self) -> list[Profile]:
        profiles = []

        if not self.directory.exists():
            return profiles

        with lock:
            files = self._list_files()

            for file in files:
                if not file.exists():
                    continue

                profile = self._parse_file(file)

                if profile:
                    profiles.append(profile)

        return profiles

    def _get_size(self) -> int:
        total = 0

        if self.directory.exists():
            with lock:
                for file in self.directory.glob('*.html'):
                    if file.exists():
                        total += file.stat().st_size

        return total

    def _list_files(self) -> list[Path]:
        files = [
            file for file in self.directory.glob('*.html')
            if file.exists()
        ]

        files.sort(
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True
        )

        return files

    def _parse_file(self, file: Path) -> Profile | None:
        stat = file.stat()
        parts = file.stem.split('_')

        timestamp, method, path_part, duration, profile_id = self._parse_filename(
            parts,
            stat
        )

        display = self._parse_path(path_part)

        mst = timezone.get_fixed_timezone(-360)
        modified = datetime.fromtimestamp(timestamp, tz=mst)

        return Profile(
            filename=file.name,
            path=display,
            method=method,
            duration=duration,
            profile_id=profile_id,
            size=self._format_size(stat.st_size),
            modified=modified.strftime('%b %d, %Y %I:%M %p MST'),
            timestamp=timestamp
        )

    def _parse_filename(self, parts: list[str], stat: Any) -> tuple[float, str, str, str, str]:
        if len(parts) >= 4:
            timestamp = int(parts[0]) / 1000
            method = parts[1]
            path_part = '_'.join(parts[2:-2])
            duration = parts[-2] if len(parts) > 3 else 'N/A'
            profile_id = parts[-1] if len(parts) > 4 else 'N/A'
        else:
            timestamp = stat.st_mtime
            method = 'Unknown'
            path_part = '_'.join(parts)
            duration = 'N/A'
            profile_id = 'N/A'

        return timestamp, method, path_part, duration, profile_id

    def _parse_path(self, path_part: str) -> str:
        if path_part == 'root':
            return '/'

        display = path_part.replace('_', '/')

        if not display.startswith('/'):
            display = '/' + display

        return display

    def _resolve_location(self) -> Path:
        location = os.getenv('PROFILING_DIR', '.profile')

        if not Path(location).is_absolute():
            base = getattr(settings, 'BASE_DIR', Path.cwd())
            location = Path(base) / location
        else:
            location = Path(location)

        return location

    def _try_delete(self, filepath: Path) -> JsonResponse | None:
        for i in range(3):
            try:
                filepath.unlink()
            except FileNotFoundError:
                return JsonResponse({'success': True, 'is_deleted': True})
            except PermissionError:
                if i < 2:
                    time.sleep(0.1)
                    continue

                return JsonResponse(
                    {'error': 'File is in use, try again'},
                    status=409
                )
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'success': True})

        return None

    def _validate_filename(self, filename: str) -> str | None:
        if '..' in filename or '/' in filename or '\\' in filename:
            return 'Invalid filename'

        if not filename.endswith('.html'):
            return 'Only HTML files are allowed'

        return None

    def _validate_filepath(self, filepath: Path, location: Path) -> str | None:
        if not filepath.is_file():
            return 'Not a file'

        try:
            filepath.resolve().relative_to(location.resolve())
        except ValueError:
            return 'Invalid file path'

        return None

    @classmethod
    def delete_file(cls, request: HttpRequest, filename: str) -> JsonResponse:
        panel = cls(None, None)
        error = panel._validate_filename(filename)

        if error:
            return JsonResponse({'error': error}, status=400)

        location = panel._resolve_location()
        filepath = location / filename

        with lock:
            if not filepath.exists():
                return JsonResponse({'success': True, 'is_deleted': True})

            error = panel._validate_filepath(filepath, location)

            if error:
                return JsonResponse({'error': error}, status=400)

            result = panel._try_delete(filepath)

            if result:
                return result

        return JsonResponse({'error': 'Could not delete file'}, status=500)

    def generate_stats(self, request: HttpRequest, response: HttpResponse) -> None:
        profiles = self._get_files()
        profiling = os.getenv('PROFILING_ENABLED', 'False') == 'True'

        stats = ProfileStats(
            profiles=[asdict(profile) for profile in profiles],
            count=len(profiles),
            directory=str(self.directory),
            total_size=self._format_size(self._get_size()),
            enabled=profiling
        )

        self.record_stats(asdict(stats))

    @classmethod
    def get_urls(cls) -> list:
        return [
            re_path(
                r'^profiling/view/(?P<filename>[^/]+)/$',
                cls.serve_file,
                name='profiling_view'
            ),
            re_path(
                r'^profiling/delete/(?P<filename>[^/]+)/$',
                csrf_exempt(cls.delete_file),
                name='profiling_delete'
            ),
            re_path(
                r'^profiling/list/$',
                cls.list_files,
                name='profiling_list'
            ),
        ]

    @classmethod
    def list_files(cls, request: HttpRequest) -> JsonResponse:
        panel = cls(None, None)
        panel.directory = panel._resolve_location()
        profiles = panel._get_files()

        response = ProfileList(
            profiles=[asdict(profile) for profile in profiles],
            count=len(profiles),
            total_size=panel._format_size(panel._get_size())
        )

        return JsonResponse(asdict(response))

    @property
    def nav_subtitle(self) -> str:
        count = 0

        if self.directory.exists():
            with lock:
                count = sum(
                    1 for f in self.directory.glob('*.html')
                    if f.exists()
                )

        return f'{count} profiles'

    @classmethod
    def serve_file(cls, request: HttpRequest, filename: str) -> HttpResponse:
        panel = cls(None, None)
        error = panel._validate_filename(filename)

        if error:
            raise Http404(error)

        location = panel._resolve_location()
        filepath = location / filename

        with lock:
            if not filepath.exists():
                message = 'Profile has been removed'
                raise Http404(message)

            error = panel._validate_filepath(filepath, location)

            if error:
                raise Http404(error)

            with open(filepath, 'r', encoding='utf-8') as handle:
                content = handle.read()

        return HttpResponse(content, content_type='text/html')
