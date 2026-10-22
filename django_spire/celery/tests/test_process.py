from __future__ import annotations

import pytest

from django_spire.celery.process import _WEB_PROCESS_ENV, is_web_server_process

_MANAGE = '/home/user/proj/manage.py'
_GUNICORN = '/usr/local/bin/gunicorn'
_CELERY_BIN = '/usr/local/bin/celery'
_CELERY_MAIN = '/home/user/proj/.venv/lib/python3.12/site-packages/celery/__main__.py'
_PYTHON = '/home/user/proj/.venv/bin/python'


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(_WEB_PROCESS_ENV, raising=False)
    monkeypatch.delenv('RUN_MAIN', raising=False)


def _check(monkeypatch: pytest.MonkeyPatch, argv: list[str], run_main: str | None = None) -> bool:
    monkeypatch.setattr('sys.argv', argv)
    if run_main is not None:
        monkeypatch.setenv('RUN_MAIN', run_main)
    return is_web_server_process()


class TestWebServerProcesses:
    def test_runserver_child_is_web(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert _check(monkeypatch, [_MANAGE, 'runserver', '0.0.0.0:8000']) is True

    def test_runserver_parent_is_not_web(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert _check(monkeypatch, [_MANAGE, 'runserver'], run_main='false') is False

    def test_runserver_plus_child_is_web(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert _check(monkeypatch, [_MANAGE, 'runserver_plus', '0.0.0.0:8000']) is True

    @pytest.mark.parametrize('binary', ['gunicorn', 'uwsgi', 'uvicorn', 'daphne', 'hypercorn'])
    def test_wsgi_asgi_binaries_are_web(self, monkeypatch: pytest.MonkeyPatch, binary: str) -> None:
        argv = [f'/usr/local/bin/{binary}', 'test_project.wsgi:application']
        assert _check(monkeypatch, argv) is True


class TestNonWebProcesses:
    def test_celery_worker_binary_is_not_web(self, monkeypatch: pytest.MonkeyPatch) -> None:
        argv = [_CELERY_BIN, '-A', 'test_project', 'worker', '-l', 'info']
        assert _check(monkeypatch, argv) is False

    def test_celery_worker_module_invocation_is_not_web(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        argv = [_CELERY_MAIN, '-A', 'test_project', 'worker', '-l', 'info']
        assert _check(monkeypatch, argv) is False

    def test_script_is_not_web(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert _check(monkeypatch, [_PYTHON, '/home/user/scripts/audit.py']) is False

    def test_unknown_binary_is_not_web(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert _check(monkeypatch, ['/usr/local/bin/some_tool', 'serve']) is False

    @pytest.mark.parametrize('command', ['migrate', 'shell', 'makemigrations'])
    def test_other_manage_commands_are_not_web(
        self, monkeypatch: pytest.MonkeyPatch, command: str
    ) -> None:
        assert _check(monkeypatch, [_MANAGE, command]) is False


class TestEnvOverride:
    def test_override_true_wins_for_script(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(_WEB_PROCESS_ENV, 'true')
        assert _check(monkeypatch, [_PYTHON, '/home/user/scripts/audit.py']) is True

    def test_override_true_wins_for_worker(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(_WEB_PROCESS_ENV, '1')
        assert _check(monkeypatch, [_CELERY_BIN, '-A', 'test_project', 'worker']) is True

    def test_override_false_wins_for_runserver(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(_WEB_PROCESS_ENV, 'false')
        assert _check(monkeypatch, [_MANAGE, 'runserver']) is False

    def test_override_false_wins_for_gunicorn(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(_WEB_PROCESS_ENV, 'no')
        assert _check(monkeypatch, [_GUNICORN, 'test_project.wsgi:application']) is False
