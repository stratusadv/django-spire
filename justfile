set windows-shell := ["powershell.exe", "-c"]
set shell := ["sh", "-c"]
set dotenv-load
set dotenv-filename := "development.env"

export PYTHONPATH := if os() == "linux" { env_var_or_default("PYTHONPATH_APPEND", "") + ":."} else { env_var_or_default("PYTHONPATH_APPEND", "") + ";." }

PYTHON := if os() == "linux" { ".venv/bin/python" } else { ".venv/Scripts/python.exe" }

default:
	just --list

celery:
	{{PYTHON}} -m celery -A test_project worker -l info --pool=threads

make-migrations:
	{{PYTHON}} ./manage.py makemigrations

migrate:
	{{PYTHON}} ./manage.py migrate

python *ARGS:
	{{PYTHON}} {{ARGS}}

run-server:
	{{PYTHON}} ./manage.py runserver

test:
	{{PYTHON}} -m pytest .

test-app app:
	{{PYTHON}} -m pytest {{app}}

test-coverage:
	{{PYTHON}} -m pytest . --cov=django_spire --cov-report=term-missing

test-coverage-app app:
	{{PYTHON}} -m pytest {{app}} --cov={{app}} --cov-report=term-missing

test-failed:
	{{PYTHON}} -m pytest --ff --lf

test-celery:
	{{PYTHON}} -m pytest django_spire/celery/tests/