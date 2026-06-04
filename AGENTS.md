# Agent Guidelines

- Always use `just` for running commands (loads environment from `development.env`)
- Run `just` to see all available commands
- Do not comment code - write it so it doesn't need comments

## Commands

```bash
# Setup (first time)
just venv              # Create .venv with uv
just make-migrations   # Create migrations
just migrate           # Run migrations
just seed              # Seed test data (superuser: stratus/stratus)

# Development
just run-server        # Start dev server (port 8000)
just celery            # Run Celery worker (separate terminal)

# Testing
just test              # All tests (-m 'not ai' by default)
just test-app <app>    # Tests for specific app
just test-coverage      # With coverage report

# Code quality
ruff check .           # Lint (uses ruff.toml config)
ruff format .           # Format code

# Docs
just docs               # Serve docs locally
```

## Testing

- `pytest` with `DJANGO_SETTINGS_MODULE=test_project.test_settings`
- Test DB uses PostgreSQL on port **5439** (configurable via `TEST_DATABASE_*` env vars)
- Markers: `ai`, `playwright`, `simulation`, `slow`, `postgres_only`
- AI tests excluded by default (`-m 'not ai'`)
- Playwright tests in `test_project/app/*/tests/test_playwright/`

## Code Quality

- **Linter**: `ruff` (config in `ruff.toml`) - ignores docstrings, complex functions
- **Format**: `ruff format` - single quotes, 100 char lines
- **CI order**: linting → tests → security (lint must pass first)

## Architecture

```
django_spire/          # Framework package (published to PyPI)
├── api/               # django-ninja REST API
├── ai/                # AI/LLM integration (chat, context)
├── auth/              # Authentication (user, api_key, mfa)
├── contrib/           # Shared: admin, breadcrumb, form, generic_views, pagination, seeding, service
├── core/              # Core: tag, middleware, management
├── file/              # Generic file management
├── help_desk/         # Ticketing system
├── history/           # History tracking
├── metric/            # Reporting framework
├── notification/      # Email, SMS, push notifications
├── theme/             # Theme management
└── ...

test_project/          # Test/demo Django project
├── app/               # Example apps (ai, celery, help_desk, infinite_scrolling, etc.)
└── settings*.py       # PostgreSQL, SQLite, test configurations
```

## App Pattern

Each `django_spire` app uses a standardized `apps.py`:

```python
class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_app_name'
    name = 'django_spire.app_name'
    REQUIRED_APPS = ('django_spire_core',)
    URLPATTERNS_INCLUDE = 'django_spire.app_name.urls'
    API_V1_ROUTER = 'django_spire.app_name.api_v1.router'  # Optional

    def ready(self) -> None:
        check_required_apps(self.label)
```

## Models

**Always use these mixins:**

```python
from django_spire.history.mixins import HistoryModelMixin

class MyModel(HistoryModelMixin):
    # Inherits: is_active, is_deleted, created_datetime, history_events
    # Provides: set_deleted(), set_active(), set_inactive()
```

**QuerySet pattern** (inherits soft-delete filters):

```python
from django_spire.history.querysets import HistoryQuerySet

class MyModelQuerySet(HistoryQuerySet):
    def active(self):
        return self.filter(is_active=True, is_deleted=False)

# On model: objects = MyModelQuerySet.as_manager()
```

## Service Layer

Business logic goes in service classes, not models. Use `BaseDjangoModelService`:

```python
from django_spire.contrib.constructor.service import BaseDjangoModelService

class MyModelService(BaseDjangoModelService['MyModel']):
    def create(self, created_by: User, **kwargs) -> MyModel:
        self.obj.created_by = created_by
        self.obj, _ = self.obj.services.save_model_obj(**kwargs)
        return self.obj

# On model: services = MyModelService()
```

## Views

Use `AppAuthController` for permission checking:

```python
from django_spire.auth.controller.controller import AppAuthController

@AppAuthController('app_name').permission_required('can_view')
def model_list_view(request):
    ...
```

Generic views available from `django_spire.contrib.generic_views`:
- `detail_view()`, `list_view()`, `form_view()`, `delete_form_view()`
- `model_form_view()` - auto breadcrumbs

## Auth Controllers

Define in `auth/controller.py` for access control:

```python
from django_spire.auth.controller.controller import BaseAuthController

class BaseAppAuthController(BaseAuthController):
    def can_add(self):
        return self.request.user.has_perm('django_spire_app.add_model')
```

## Test Base

```python
from django_spire.core.tests.test_cases import BaseTestCase

class MyTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()  # Includes logged-in super_user in self.client
```

## Seeding

Define seeders for test data:

```python
from django_spire.contrib.seeding import DjangoModelSeeder

class MyModelSeeder(DjangoModelSeeder):
    fields = {
        'name': ('faker', 'name'),
        'owner_id': ('custom', 'fk_random', {'model_class': User}),
    }
```

## Environment

- `development.env` sets all local defaults (database, AWS, AI APIs, Twilio, Celery)
- `DANDY_SETTINGS_MODULE=test_project.dandy_settings`

## Reference Examples

- **Full app**: `test_project/app/help_desk/`
- **Service pattern**: `test_project/app/model_and_service/`
- **API**: `django_spire/api/api_v1.py` (auto-discovers routers)
- **URLs**: `django_spire/urls.py` (auto-discovers app URLs)