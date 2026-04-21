set windows-shell := ["powershell.exe", "-c"]
set shell := ["sh", "-c"]
set dotenv-load
set dotenv-filename := "development.env"

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

test-last-failed:
	{{PYTHON}} -m pytest --ff --lf

test-coverage:
	{{PYTHON}} -m pytest . --cov=app --cov-report=term-missing --cov-report=html:.test_coverage/