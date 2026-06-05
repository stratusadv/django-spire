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
	bun add bootstrap
	bun sass --load-path=node_modules django_spire/core/static/django_spire/scss/default.scss django_spire/core/static/django_spire/css/bootstrap.css

themes:
	bun sass --load-path=node_modules django_spire/core/static/django_spire/scss/themes/_default.scss django_spire/core/static/django_spire/css/default.css
	bun sass --load-path=node_modules django_spire/core/static/django_spire/scss/themes/_nord.scss django_spire/core/static/django_spire/css/nord.css
	bun sass --load-path=node_modules django_spire/core/static/django_spire/scss/themes/_gruvbox.scss django_spire/core/static/django_spire/css/gruvbox.css
	bun sass --load-path=node_modules django_spire/core/static/django_spire/scss/themes/_catppuccin.scss django_spire/core/static/django_spire/css/catppuccin.css
	bun sass --load-path=node_modules django_spire/core/static/django_spire/scss/themes/_palenight.scss django_spire/core/static/django_spire/css/palenight.css
	bun sass --load-path=node_modules django_spire/core/static/django_spire/scss/themes/_tokyo-night.scss django_spire/core/static/django_spire/css/tokyo-night.css
	bun sass --load-path=node_modules django_spire/core/static/django_spire/scss/themes/_rose-pine.scss django_spire/core/static/django_spire/css/rose-pine.css
	bun sass --load-path=node_modules django_spire/core/static/django_spire/scss/themes/_one-dark.scss django_spire/core/static/django_spire/css/one-dark.css
	bun sass --load-path=node_modules django_spire/core/static/django_spire/scss/themes/_material.scss django_spire/core/static/django_spire/css/material.css
	bun sass --load-path=node_modules django_spire/core/static/django_spire/scss/themes/_ayu.scss django_spire/core/static/django_spire/css/ayu.css
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
