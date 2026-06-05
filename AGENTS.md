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
just scss              # Compile SCSS to CSS

# Testing
just test              # All tests (-m 'not ai' by default)
just test-app <app>    # Tests for specific app
just test-coverage     # With coverage report

# Code quality
ruff check .           # Lint (uses ruff.toml config)
ruff format .          # Format code

# Docs
just docs              # Serve docs locally
just docs-tests        # Build docs with strict mode
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
├── ai/                # AI/LLM integration (chat, context, sms)
├── api/               # django-ninja REST API (ApiAccess model, API key auth)
├── auth/              # Authentication (user, api_key, mfa, group)
├── celery/            # Celery task queue support
├── changelog/          # Changelog tracking
├── comment/            # Comment system
├── contrib/            # Shared utilities (see Contrib Packages below)
├── core/               # Core: tag, middleware, management, tests
├── file/              # Generic file management
├── help_desk/         # Ticketing system
├── history/           # History tracking (HistoryModelMixin, HistoryQuerySet)
├── knowledge/         # Knowledge base
├── metric/            # Reporting framework
├── notification/      # Email, SMS, push notifications
├── settings.py        # Default settings
├── sync/              # Data synchronization (tablet/cloud)
├── testing/           # Testing utilities (playwright fixtures)
├── theme/             # Theme management
└── urls.py            # Auto-discovers app URLs

test_project/          # Test/demo Django project
├── app/               # Example apps
│   ├── ai/, celery/, comment/, core/, file/, help_desk/
│   ├── history/, home/, infinite_scrolling/, knowledge/
│   ├── lazy_tabs/, model_and_service/, notification/, ordering/
│   ├── queryset_filtering/, rest/, sync/, tabular/, wizard/
├── base_settings.py   # Base configuration
├── postgres_settings.py  # PostgreSQL config
├── dandy_settings.py  # Dandy-specific config
├── sqlite_settings.py # SQLite config
├── test_settings.py   # Test configuration
└── seed.py            # Test data seeding
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
    API_V1_ROUTER_PREFIX = 'prefix'  # Optional, required with API_V1_ROUTER

    def ready(self) -> None:
        check_required_apps(self.label)
```

Apps with model permissions must include `MODEL_PERMISSIONS`:

```python
MODEL_PERMISSIONS = ({
    'name': 'app_name',
    'verbose_name': 'App Name',
    'model_class_path': 'django_spire.app_name.models.MyModel',
    'is_proxy_model': False,
})
```

## Models

### HistoryModelMixin

Always use this mixin for models that need soft-delete and history tracking:

```python
from django_spire.history.mixins import HistoryModelMixin

class MyModel(HistoryModelMixin):
    # Inherits: is_active, is_deleted, created_datetime, history_events
    # Auto-creates CREATED/UPDATED events on save
    # Methods: set_deleted(), set_active(), set_inactive(), un_set_deleted()
    ...
```

### HistoryQuerySet

Use for filtered querysets:

```python
from django_spire.history.querysets import HistoryQuerySet

class MyModelQuerySet(HistoryQuerySet):
    def active(self):
        return self.filter(is_active=True, is_deleted=False)

# On model: objects = MyModelQuerySet.as_manager()
```

Available filters: `active()`, `inactive()`, `deleted()`, `not_deleted()`

### ActivityMixin

For activity/feed tracking:

```python
from django_spire.core.models import ActivityMixin

class MyModel(ActivityMixin, HistoryModelMixin):
    # Inherits: activities GenericRelation
    # Methods: add_activity(user, verb, information, recipient, subscribers)
    # Property: creator - returns first user to create activity
    ...
```

## Service Layer

Business logic goes in service classes, not models.

### BaseDjangoModelService

```python
from django_spire.contrib.constructor.service import BaseDjangoModelService

class MyModelService(BaseDjangoModelService['MyModel']):
    def create(self, created_by: User, **kwargs) -> MyModel:
        self.obj.created_by = created_by
        self.obj, _ = self.obj.services.save_model_obj(**kwargs)
        return self.obj

# On model: services = MyModelService()
```

### save_model_obj()

Core save method that handles all field types:

```python
# Returns (saved_obj, was_created)
obj, created = my_model.services.save_model_obj(field1='value', fk_id=pk)
```

### Sub-services

```python
class AdultService(BaseDjangoModelService['Adult']):
    sub: AdultSubService = AdultSubService()

class AdultSubService:
    def full_name(self) -> str:
        return f"{self.obj.first_name} {self.obj.last_name}"

# Usage: adult.services.sub.full_name()
```

### Service Attachment Pattern

```python
from django_spire.core.mixins import ActivityMixin

class Adult(ActivityMixin, HistoryModelMixin):
    services = AdultService()
```

## URL Patterns

URLs are auto-discovered from app `URLPATTERNS_INCLUDE`. Namespaced patterns:

```
django_spire:{app}:{namespace}:{view}
django_spire:{app}:{namespace}:list
django_spire:{app}:{namespace}:detail
django_spire:{app}:{namespace}:create
django_spire:{app}:{namespace}:update
django_spire:{app}:{namespace}:delete
```

Standard namespace structure for apps:
- `page:` - List/detail views
- `form:` - Create/update forms

## API (django-ninja)

API v1 auto-discovers routers from apps with `API_V1_ROUTER` and `API_V1_ROUTER_PREFIX`:

```python
# App with API
API_V1_ROUTER = 'django_spire.app_name.api_v1.router'
API_V1_ROUTER_PREFIX = 'app'
```

API access controlled via `ApiAccess` model with `ApiKeySecurity`:

```python
from django_spire.api.auth.security import ApiKeySecurity

api_v1 = NinjaAPI(auth=[ApiKeySecurity(permission_required=ApiPermissionChoices.VIEW)])
```

## Choices

Use Django TextChoices for choice fields:

```python
from django.db import models

class HelpDeskTicketPriorityChoices(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'med', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urge', 'Urgent'
```

IntegerChoices for permission levels:

```python
from django.db import models

class ApiPermissionChoices(models.IntegerChoices):
    VIEW = 1, 'View'
    ADD = 2, 'Add'
    CHANGE = 3, 'Change'
    DELETE = 4, 'Delete'
```

## Auth Controllers

Define in `auth/controller.py` for access control:

```python
from django_spire.auth.controller.controller import BaseAuthController

class BaseAppAuthController(BaseAuthController):
    def can_add(self):
        return self.request.user.has_perm('django_spire_app.add_model')
```

Use in views:

```python
from django_spire.auth.controller.controller import AppAuthController

@AppAuthController('app_name').permission_required('can_view')
def model_list_view(request):
    ...

@AppAuthController('app_name').permission_required('can_delete', all_required=False)
def some_view(request):
    # any of the permissions required
```

## Views

### Permission-protected Views

```python
from django_spire.auth.controller.controller import AppAuthController

@AppAuthController('help_desk').permission_required('can_view')
def ticket_detail_view(request, pk):
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)
    return generic_views.detail_view(request, obj=ticket, ...)
```

### Generic Views

```python
from django_spire.contrib.generic_views import (
    detail_view, list_view, form_view, delete_form_view, model_form_view
)

# detail_view - renders object detail page
# list_view - renders object list
# form_view - renders generic form
# delete_form_view - confirmation form before delete
# model_form_view - auto breadcrumbs, returns form view with model context
```

### Modal Views

```python
from django_spire.contrib.generic_views.modal_views import (
    dispatch_modal_delete_form_content,
    dispatch_confirmation_modal_form_content,
)
```

## Breadcrumbs

```python
from django_spire.contrib.breadcrumb.breadcrumbs import Breadcrumbs

breadcrumb = Breadcrumbs()
breadcrumb.add_breadcrumb('Home', '/')
breadcrumb.add_obj_breadcrumbs(obj)  # Uses obj.breadcrumbs()
breadcrumb.add_form_breadcrumbs(obj)  # Creates edit/create breadcrumbs
breadcrumb.add_base_breadcrumb(MyModel)  # Uses model.base_breadcrumb()
```

## Forms

### Confirmation Forms

```python
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm, ConfirmationForm

class DeleteConfirmationForm(forms.Form):
    should_delete = forms.BooleanField(required=False, initial=False)

    def save(self, user, verbs, delete_func=None, activity_func=None, auto_add_activity=True):
        if self.cleaned_data['should_delete']:
            delete_func()

class ConfirmationForm(forms.Form):
    should_confirm = forms.BooleanField(required=False, initial=False)
```

## Test Base

```python
from django_spire.core.tests.test_cases import BaseTestCase

class MyTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()  # Creates super_user, force_login to self.client
```

## Seeding

Define seeders for test data:

```python
from django_spire.contrib.seeding import DjangoModelSeeder

class HelpDeskTicketSeeder(DjangoModelSeeder):
    model_class = HelpDeskTicket
    fields = {
        'id': 'exclude',
        'description': ('llm', 'Help desk ticket description'),
        'created_by_id': ('custom', 'fk_random', {'model_class': AuthUser}),
        'created_datetime': ('custom', 'date_time_between', {'start_date': '-30d', 'end_date': 'now'}),
    }
```

### Field Seeders

| Type | Usage | Example |
|------|-------|---------|
| `faker` | Faker data | `('faker', 'name')` |
| `custom` | Custom functions | `('custom', 'fk_random', {'model_class': User})` |
| `static` | Static values | `('static', 'some_value')` |
| `llm` | AI-generated | `('llm', 'Description prompt')` |

## Contrib Packages

| Package | Purpose | Key Files |
|---------|---------|-----------|
| `breadcrumb` | Breadcrumb navigation | `breadcrumbs.py` |
| `form` | Form utilities | `confirmation_forms.py`, `tools.py` |
| `constructor` | Model construction | `django_model_service.py` |
| `generic_views` | Reusable views | `page_views.py`, `modal_views.py` |
| `pagination` | Pagination | Various utilities |
| `seeding` | Test data | `django/seeder.py`, `field/` |
| `ordering` | Sort ordering | Various utilities |
| `queryset` | Query utilities | Various utilities |
| `rest` | REST utilities | Various utilities |

## Settings

| File | Purpose |
|------|---------|
| `base_settings.py` | Base configuration, loads `development.env` |
| `postgres_settings.py` | PostgreSQL database config |
| `test_settings.py` | pytest config, TEST_DATABASE_* env vars |
| `dandy_settings.py` | Dandy-specific config |

## Environment

- `development.env` - Local defaults (database, AWS, AI APIs, Twilio, Celery)
- `DJANGO_SETTINGS_MODULE` - Points to active settings module
- `TEST_DATABASE_*` - Override test DB (5439 default)

## Frontend Libraries

The project uses CDN-hosted JavaScript libraries loaded in the base template (`django_spire/core/templates/django_spire/base/base.html`).

### Alpine.js (Primary JS Framework)

Alpine.js is the primary frontend framework for reactivity. Plugins are loaded as defer scripts:

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/intersect@3.14.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/mask@3.14.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/collapse@3.14.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.14.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.14.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/sort@3.x.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.x/dist/cdn.min.js"></script>
```

**Alpine.js Usage Pattern:**

```html
<div x-data="{
    service_add: new GlueCharField('service_add'),
    response_message: '',
    async init() { ... },
    async handle_submit() { ... }
}">
    <form x-ref="upload_form">...</form>
    <button @click="handle_submit()">Submit</button>
    <pre x-text="response_message"></pre>
</div>
```

### Django Glue Integration

`django_glue` provides server-side data binding with Alpine.js:

```html
{% load django_glue %}
{% glue_model object_name="my_object" %}
    <span>{{ my_object.field }}</span>
{% endglue_model %}
```

Available glue tags: `{% glue_model %}`, `{% glue_queryset %}`, `{% glue_list %}`, `{% glue_form %}`

### Bootstrap 5.3

CSS framework and JavaScript components:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.x/dist/css/bootstrap.min.css">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.x/dist/js/bootstrap.bundle.min.js"></script>
```

Custom overrides: `django_spire/css/bootstrap-override.css`
Extensions: `django_spire/css/bootstrap-extension.css`

### Bootstrap Icons

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.x/font/bootstrap-icons.min.css">
```

### Flatpickr

Date/time picker:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
```

### ECharts

Charts and visualizations:

```html
<script defer src="https://cdn.jsdelivr.net/npm/echarts@5.4.x/dist/echarts.min.js"></script>
```

### Axios

HTTP client for API requests:

```html
<script defer src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
```

### Pulltorefresh.js

iOS-style pull to refresh:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/pulltorefreshjs/0.1.22/index.umd.min.js"></script>
```

### Theme System

Themes are defined in `django_spire/theme/` and support light/dark modes. The base template includes theme configuration:

```html
<html lang="en" data-theme="{{ theme.mode }}" data-theme-family="{{ theme.family }}">
```

Custom CSS files: `app-light.css`, `app-dark.css` in `test_project/static/css/`

### SCSS

SCSS is compiled using Dart Sass via `bun`. Bootstrap SCSS is included as a local dependency to allow customization.

```bash
just scss   # Compiles SCSS to CSS
```

- SCSS source: `django_spire/core/static/django_spire/scss/`
- Output CSS: `django_spire/core/static/django_spire/css/default.css`
- Bootstrap imported via `--load-path=node_modules`
- Add new Bootstrap versions: `bun add bootstrap`

## Reference Examples

| Pattern | Location |
|---------|----------|
| Full app | `test_project/app/help_desk/` |
| Service layer | `test_project/app/model_and_service/` |
| API | `django_spire/api/api_v1.py` |
| URLs | `django_spire/urls.py` |
| Choices | `django_spire/help_desk/choices.py` |
| Auth controller | `django_spire/help_desk/auth/controller.py` |