set windows-shell := ["powershell.exe", "-c"]
set shell := ["sh", "-c"]
set dotenv-load
set dotenv-filename := "development.env"

export PYTHONPATH := if os() == "linux" { env_var_or_default("PYTHONPATH_APPEND", "") + ":." } else { env_var_or_default("PYTHONPATH_APPEND", "") + ";." }
PYTHON := if os() == "linux" { ".venv/bin/python" } else { ".venv/Scripts/python.exe" }
MKDOCS := if os() == "linux" { ".venv/bin/mkdocs" } else { ".venv/Scripts/mkdocs.exe" }

default:
    just --list
celery:
    {{ PYTHON }} -m celery -A test_project worker -l info --pool=threads
docs:
    {{ MKDOCS }} serve
docs-tests:
    {{ MKDOCS }} build --strict
[windows]
demo NAME="" SPEED="normal":
    $env:DANDY_SETTINGS_MODULE='test_project.dandy_settings'; $env:DEMO_MODE='narrate'; $env:DEMO_SPEED='{{SPEED}}'; {{PYTHON}} -m pytest -m demo --headed --video off {{ if NAME == "" { "" } else { "-k '" + replace(NAME, "-", "_") + "'" } }}
[unix]
demo NAME="" SPEED="normal":
    DANDY_SETTINGS_MODULE=test_project.dandy_settings DEMO_MODE=narrate DEMO_SPEED={{SPEED}} {{PYTHON}} -m pytest -m demo --headed --video off {{ if NAME == "" { "" } else { "-k '" + replace(NAME, "-", "_") + "'" } }}
[windows]
demo-video NAME="" SPEED="normal":
    $env:DANDY_SETTINGS_MODULE='test_project.dandy_settings'; $env:DEMO_MODE='narrate'; $env:DEMO_SPEED='{{SPEED}}'; $env:DEMO_VIDEO='1'; $ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue; if ($ffmpeg) { $env:PLAYWRIGHT_VIDEO_FFMPEG = $ffmpeg.Source; $env:PLAYWRIGHT_VIDEO_FPS = '60' }; {{PYTHON}} -m pytest -m demo --video on {{ if NAME == "" { "" } else { "-k '" + replace(NAME, "-", "_") + "'" } }}
[unix]
demo-video NAME="" SPEED="normal":
    #!/usr/bin/env bash
    export DANDY_SETTINGS_MODULE=test_project.dandy_settings DEMO_MODE=narrate DEMO_SPEED={{SPEED}} DEMO_VIDEO=1
    if command -v ffmpeg >/dev/null; then export PLAYWRIGHT_VIDEO_FFMPEG="$(command -v ffmpeg)" PLAYWRIGHT_VIDEO_FPS=60; fi
    {{PYTHON}} -m pytest -m demo --video on {{ if NAME == "" { "" } else { "-k '" + replace(NAME, "-", "_") + "'" } }}
demos:
    DANDY_SETTINGS_MODULE=test_project.dandy_settings {{ PYTHON }} -m pytest -m demo --collect-only -q
make-migrations:
    {{ PYTHON }} ./manage.py makemigrations
migrate:
    {{ PYTHON }} ./manage.py migrate
opencode:
    ./.venv/Scripts/activate.bat; if ($?) { opencode . }
python *ARGS:
    {{ PYTHON }} {{ ARGS }}
run-server:
    {{ PYTHON }} ./manage.py runserver
scss:
    {{ PYTHON }} ./manage.py spire_compile_scss
test:
    {{ PYTHON }} -m pytest . --reuse-db
test-app app:
    {{ PYTHON }} -m pytest {{ app }} --reuse-db
test-coverage:
    {{ PYTHON }} -m pytest . --cov=django_spire --cov-report=term-missing --reuse-db
test-coverage-app app:
    {{ PYTHON }} -m pytest {{ app }} --cov={{ app }} --cov-report=term-missing --reuse-db
test-failed:
    {{ PYTHON }} -m pytest --ff --lf --reuse-db
test-parallel workers="auto":
    {{ PYTHON }} -m pytest . -n {{ workers }} --reuse-db
test-serial:
    {{ PYTHON }} -m pytest . -n 0 --reuse-db
seed:
    {{ PYTHON }} test_project/seed.py
venv:
    uv venv --clear .venv
    uv sync --all-extras --upgrade
venv-upgrade:
    uv sync --all-extras --upgrade
