set windows-shell := ["powershell.exe", "-c"]
set shell := ["sh", "-c"]
set dotenv-load
set dotenv-filename := "development.env"

export PYTHONPATH := if os() == "linux" { env_var_or_default("PYTHONPATH_APPEND", "") + ":." } else { env_var_or_default("PYTHONPATH_APPEND", "") + ";." }
PYTHON := if os() == "linux" { ".venv/bin/python" } else { ".venv/Scripts/python.exe" }

default:
    just --list
celery:
    {{ PYTHON }} -m celery -A test_project worker -l info --pool=threads
docs:
    mkdocs serve
docs-tests:
    mkdocs build --strict
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
seed:
    {{ PYTHON }} test_project/seed.py
venv:
    uv venv --clear .venv
    uv sync --all-extras --upgrade
venv-upgrade:
    uv sync --all-extras --upgrade
