# Agent

## Guidelines
- Always look for relevant skills to load
- Do not comment your code. You should never write anything complicated enough that needs comments.

## Project Overview
- A core Django application
- Rich UI components using Bootstrap 5 integration
- Integration with external services like SendGrid for email and AWS S3 for storage

## Architecture

The application follows a modular Django structure with:
- Core app structure under `app` directory
- System configurations in `system/` (development, testing, production)
- Static assets in `static_files/` and templates in `templates/`


Key components:
- `django_spire` framework for core functionality (auth, notifications, themes)
- Modular settings configuration (`system/development`, `system/testing`, `system/production`)

## Code Structure

- `app` - Main application modules (home, user_profile)
- `system/` - System-wide configuration (development, testing, production)
- `templates/` - HTML templates using Django template inheritance
- `static_files/` - Static assets including CSS, JS, images, fonts
- `manage.py` - Django management script

## Technology Stack

- Backend: Python, Django 5.0+
- Frontend: HTML, CSS, JavaScript, Bootstrap 5, Alpine js
- Database: PostgreSQL
- Hosting: Gunicorn (production)
- Storage: AWS S3
- Email: SendGrid
