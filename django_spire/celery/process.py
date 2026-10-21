from __future__ import annotations

import os
import sys
from pathlib import Path

_SERVER_COMMANDS = frozenset({'runserver', 'runserver_plus'})


def is_web_server_process() -> bool:
    if os.environ.get('RUN_MAIN', 'true') == 'false':
        return False

    if Path(sys.argv[0]).name != 'manage.py':
        return True

    command = next((arg for arg in sys.argv[1:] if not arg.startswith('-')), '')
    return command in _SERVER_COMMANDS
