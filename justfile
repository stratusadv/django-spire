set windows-shell := ["powershell.exe", "-c"]
set shell := ["sh", "-c"]
set dotenv-load
set dotenv-filename := "development.env"

PYTHON := if os() == "linux" { ".venv/bin/python" } else { ".venv/Scripts/python.exe" }

default:
	just --list

celery:
	{{PYTHON}} -m celery -A test_project worker -l info --pool=threads

