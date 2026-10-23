from __future__ import annotations

import os
import sys
from pathlib import Path

_SERVER_COMMANDS = frozenset({'runserver', 'runserver_plus'})
_WEB_SERVER_BINARIES = frozenset({'gunicorn', 'uwsgi', 'uvicorn', 'daphne', 'hypercorn'})
_WEB_PROCESS_ENV = 'DJANGO_SPIRE_CELERY_WEB_PROCESS'


def is_web_server_process() -> bool:
    override = os.environ.get(_WEB_PROCESS_ENV, '').strip().lower()
    if override in {'true', '1', 'yes'}:
        return True
    if override in {'false', '0', 'no'}:
        return False

    if os.environ.get('RUN_MAIN', 'true') == 'false':
        return False

    if Path(sys.argv[0]).name == 'manage.py':
        command = next((arg for arg in sys.argv[1:] if not arg.startswith('-')), '')
        return command in _SERVER_COMMANDS

    return Path(sys.argv[0]).name in _WEB_SERVER_BINARIES
