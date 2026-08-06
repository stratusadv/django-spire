# Agent Guidelines

- Always use `just` for running commands (loads `development.env`)
- Run `just` to see all available commands
- Do not comment code - write it so it doesn't need comments

## Commands

```bash
# Setup (first time)
just venv              # Create .venv with uv, then uv sync --all-extras
just venv-upgrade      # uv sync --all-extras --upgrade
just make-migrations   # python manage.py makemigrations
just migrate           # python manage.py migrate
just seed              # Seed test data (superuser: stratus/stratus)

# Development
just run-server        # Dev server
just celery            # Celery worker (threads pool)
just scss              # Compile SCSS to django-spire-bootstrap.css
just python <args>     # Run venv python

# Testing
just test                    # pytest . --reuse-db (-n 12, excludes ai & playwright)
just test-app <app>          # Tests for a specific app or directory
just test-coverage           # Coverage of django_spire
just test-coverage-app <app> # Coverage of a specific app
just test-failed             # Failed tests first (--ff --lf)
just test-parallel [n]       # pytest -n <n> (default: auto)
just test-serial             # pytest -n 0 (no parallel)

# Code quality
ruff check .           # Lint (uses ruff.toml config)
ruff format .          # Format code

# Docs
just docs              # Serve docs locally (mkdocs)
just docs-tests        # Build docs with strict mode
```

## Testing

- `pytest` with `DJANGO_SETTINGS_MODULE=test_project.test_settings`
- Test DB uses PostgreSQL on localhost port **5439** (database `django_spire_test`, overridable via `TEST_DATABASE_*` env vars)
- Markers: `ai`, `playwright`, `simulation`, `slow`, `postgres_only`
- Default addopts in `pyproject.toml`: `-v --tb=short -n 12 --ds=test_project.test_settings -m 'not ai and not playwright'` (both AI **and** Playwright tests are excluded by default)
- `just test*` recipes add `--reuse-db`
- Playwright tests live under `test_playwright/` directories (skipped by `norecursedirs`); run config in `test_project/playwright.config.py`, reusable fixtures/pages/components in `django_spire/testing/playwright/`
- CI (`.github/workflows/ci.yml`): boots Postgres via `test_project/docker-compose.test.yml`, runs pytest excluding `test_playwright`

## Code Quality

- **Linter**: `ruff` (config in `ruff.toml`) - `select = ["ALL"]` with ignores (docstrings `D*`, `C901` complexity, etc.), max complexity 6
- **Format**: `ruff format` - single quotes, 100 char lines, 4 space indent
- **CI order**: linting → tests → security (lint must pass first)

## Architecture

```
django_spire/          # Framework package (published to PyPI)
├── ai/                # AI/LLM integration (chat router + intelligence, context, sms)
├── api/               # django-ninja REST API (ApiAccess model, ApiKeySecurity, throttling)
├── auth/              # Authentication (user, group, mfa, permissions, controller)
├── celery/            # Celery task queue support
├── comment/           # Comment system
├── conf.py            # Settings wrapper (project settings + django_spire defaults)
├── constants.py       # __VERSION__, BASE_URL_NAME
├── contrib/           # Shared utilities (see Contrib Packages below)
├── core/              # Core: tag, middleware, management commands, SCSS, templatetags, tests
├── exceptions.py      # DjangoSpireConfigurationError, etc.
├── file/              # Generic file management
├── help_desk/         # Ticketing system
├── history/           # History tracking (HistoryModelMixin, HistoryQuerySet, activity, viewed)
├── knowledge/         # Knowledge base (collection, entry, intelligence)
├── metric/            # Reporting framework (domain, report, visual)
├── notification/      # App, email, SMS, push notifications (automations, processors)
├── settings.py        # DJANGO_SPIRE_* default settings
├── shortcuts.py
├── sync/              # Data synchronization (core, database, django, file)
├── testing/           # Testing utilities (playwright fixtures, pages, components)
├── tools.py           # check_required_apps(), app_is_installed()
└── urls.py            # Auto-discovers app URLs

test_project/          # Test/demo Django project
├── app/               # Example apps
│   ├── ai/, celery/, comment/, core/, file/, help_desk/
│   ├── history/, home/, knowledge/, landing/, model_and_service/
│   ├── notification/, ordering/, rest/, sync/, task/
├── base_settings.py   # Base configuration, loads development.env
├── postgres_settings.py  # PostgreSQL database config
├── dandy_settings.py  # Dandy-specific config
├── sqlite_settings.py # SQLite config
├── test_settings.py   # Test configuration (TEST_DATABASE_* env vars)
├── seed.py            # Test data seeding
├── celery.py, worker.py, asgi.py, wsgi.py  # Process entry points
├── static_files/      # Static files + compiled SCSS output
├── templates/         # Test project templates
├── docs/              # MkDocs source
├── docker-compose.test.yml  # CI test database
└── playwright.config.py     # Playwright run config
```

## App Pattern

Each `django_spire` app uses a standardized `apps.py`. `python manage.py spire_startapp <app>` scaffolds a new app (models, services, page/form views, urls, seeding, tests, templates) interactively:

```python
from django.apps import AppConfig

from django_spire.tools import check_required_apps


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_app_name'
    name = 'django_spire.app_name'
    MODEL_PERMISSIONS = (
        {
            'name': 'app_name',
            'verbose_name': 'App Name',
            'model_class_path': 'django_spire.app_name.models.MyModel',
            'is_proxy_model': False,
        },
    )
    REQUIRED_APPS = ('django_spire_core',)
    URLPATTERNS_INCLUDE = 'django_spire.app_name.urls'
    URLPATTERNS_NAMESPACE = 'app_name'
    API_V1_ROUTER = 'django_spire.app_name.api_v1.router'  # Optional
    API_V1_ROUTER_PREFIX = 'prefix'  # Required with API_V1_ROUTER

    def ready(self) -> None:
        check_required_apps(self.label)
```

`URLPATTERNS_INCLUDE` + `URLPATTERNS_NAMESPACE` are auto-discovered by `django_spire/urls.py`.

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
from django_spire.history.activity.mixins import ActivityMixin

class MyModel(ActivityMixin, HistoryModelMixin):
    # Inherits: activities GenericRelation
    # Methods: add_activity(user, verb, information, recipient, subscribers)
    # Property: creator - returns first user to create activity
    ...
```

See `django_spire/history/activity/mixins.py`.

## Service Layer

Business logic goes in service classes, not models.

### BaseDjangoModelService

```python
from django_spire.contrib.constructor.service import BaseDjangoModelService

class MyModelService(BaseDjangoModelService['MyModel']):
    obj: MyModel

    def create(self, created_by: User, **kwargs) -> MyModel:
        self.obj.created_by = created_by
        self.obj, _ = self.obj.services.save_model_obj(**kwargs)
        return self.obj

# On model: services = MyModelService()
```

### save_model_obj()

Core save method that handles all field types (including M2M):

```python
# Returns (saved_obj, was_created)
obj, created = my_model.services.save_model_obj(field1='value', fk_id=pk)
```

### Sub-services

```python
class AdultService(BaseDjangoModelService['Adult']):
    obj: Adult
    sub: AdultSubService = AdultSubService()

class AdultSubService(BaseDjangoModelService['Adult']):
    obj: Adult

    def full_name(self) -> str:
        return f'{self.obj.first_name} {self.obj.last_name}'

# Usage: adult.services.sub.full_name()
```

### Service Attachment Pattern

```python
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin

class Adult(ActivityMixin, HistoryModelMixin):
    services = AdultService()
```

See `test_project/app/model_and_service/` for a full example.

## URL Patterns

URLs are auto-discovered from app `URLPATTERNS_INCLUDE` + `URLPATTERNS_NAMESPACE`. Apps split URL configuration into page/form modules:

```python
# app/urls/__init__.py
from django.urls import path, include

app_name = 'task'

urlpatterns = [
    path('page/', include('test_project.app.task.urls.page_urls', namespace='page')),
    path('form/', include('test_project.app.task.urls.form_urls', namespace='form')),
]
```

Namespaced patterns (names inside each module use `app_name = 'page'` / `'form'`):

```
{app}:page:list
{app}:page:detail
{app}:form:form
{app}:form:delete
{app}:form:create_modal
{app}:form:update_modal
{app}:form:delete_modal
```

Framework apps are mounted under the `django_spire:` namespace (e.g. `django_spire:api:page:list`, `django_spire:auth:admin:login`).

## API (django-ninja)

The shared `NinjaAPI` instance is in `django_spire/api/api_v1.py` and is mounted at `api/v1/`. Routers auto-discover from apps with `API_V1_ROUTER` and `API_V1_ROUTER_PREFIX`:

```python
# App with API
API_V1_ROUTER = 'django_spire.app_name.api_v1.router'
API_V1_ROUTER_PREFIX = 'app'
```

API access controlled via `ApiAccess` model with `ApiKeySecurity`:

```python
from ninja import NinjaAPI
from ninja.throttling import AnonRateThrottle, AuthRateThrottle

from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.choices import ApiPermissionChoices

api_v1 = NinjaAPI(
    title='API',
    version='1.0',
    urls_namespace='django_spire:api_v1',
    auth=[ApiKeySecurity(permission_required=ApiPermissionChoices.DELETE)],
    throttle=[AnonRateThrottle('1/s'), AuthRateThrottle('150/s')],
)
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

Path: `django_spire/api/choices.py`

## Auth Controllers

Define in `auth/controller.py` for access control:

```python
from django_spire.auth.controller.controller import BaseAuthController

class BaseAppAuthController(BaseAuthController):
    def can_add(self) -> bool:
        return self.request.user.has_perm('django_spire_app.add_model')
```

Use in views (also validates the `can_*` methods exist):

```python
from django_spire.auth.controller.controller import AppAuthController

@AppAuthController('app_name').permission_required('can_view')
def model_list_view(request):
    ...

@AppAuthController('app_name').permission_required('can_delete', all_required=False)
def some_view(request):
    # any of the permissions required
```

Controllers can be registered globally so they are exposed to templates:

```python
DJANGO_SPIRE_AUTH_CONTROLLERS = {
    'app_name': 'path.to.KnowledgeAuthController',
}
```

Defaults live in `django_spire/settings.py`. The context processor then injects `AuthController` for use in templates:

```html
{% if AuthController.app_name.can_add %}
```

## Views

### Standard View Pattern

Views are plain function-based views using a `Navigation` subclass, `django-glue` data binding, and `TemplateResponse`:

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django_glue import Glue

from django_spire.contrib.shortcuts import get_object_or_null_obj
from test_project.app.task.navigation import TaskNavigation
from test_project.app.task import forms, models


@login_required()
def list_view(request):
    tasks = models.Task.objects.active().prefetch_users()

    Glue.queryset(
        request,
        'tasks',
        tasks,
        Glue.Access.CHANGE,
        fields=['id', 'name', 'status', 'created_datetime'],
        form=forms.TaskModelForm(),
    )

    nav = TaskNavigation()
    nav.set_page_title_from_model_plural_name(models.Task)

    context = nav.as_context()
    context['task_count'] = tasks.count()

    return TemplateResponse(request, context=context, template='task/page/list_page.html')
```

Form view (create + update with `get_object_or_null_obj`):

```python
@login_required()
def form_view(request, pk):
    task = get_object_or_null_obj(models.Task, pk=pk)
    form = forms.TaskModelForm(request.POST or None, instance=task)

    Glue.form(request, 'new_task_form', form, Glue.Access.DELETE)

    nav = TaskNavigation()
    nav.set_page_title_to_form_action_from_model_instance(task)
    nav.breadcrumbs.add(f'{task.name}' if task.pk else 'New Task')

    return TemplateResponse(request, context={**nav.as_context()}, template='task/page/form_page.html')
```

Delete view (soft delete + activity):

```python
@login_required()
def delete_view(request, pk):
    task = get_object_or_404(models.Task, pk=pk)
    return_url = request.GET.get('return_url', reverse('task:page:list'))

    if request.method == 'POST':
        task.set_deleted()
        task.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted task {task.name}.',
        )
        return redirect(return_url)

    nav = TaskNavigation()
    nav.page_title = f'Delete {task.name}'
    return TemplateResponse(request, context={**nav.as_context(), 'task': task}, template='task/page/delete_page.html')
```

### Modal Views

Modal views are separate views that return the modal `content/` fragment (invoked client-side via `Spire.modal`); create/update use `Glue.model`:

```python
def create_modal_view(request):
    task = get_object_or_null_obj(models.Task)

    Glue.model(request, 'task', task, Glue.Access.CHANGE,
               fields=['name', 'description', 'status'], form_class=forms.TaskModelForm)

    return TemplateResponse(request, context={'task': task, 'glue_form': 'Glue.model.task.form'},
                            template='task/modal/content/task_form_modal_content.html')
```

Useful contrib helpers:
- `django_spire.contrib.shortcuts.get_object_or_null_obj(...)` - get object or a blank instance
- `django_spire.contrib.redirects.safe_redirect_url(request, fallback=...)` - safe return redirect

## Breadcrumbs

Breadcrumbs are provided by a `Navigation` subclass (see `django_spire/contrib/navigation/`):

```python
from django_spire.contrib.navigation.navigation import Navigation


class TaskNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-list-task'
        self.breadcrumbs.add('Tasks', 'task:page:list')
```

Available on `nav`:

```python
nav.page_title                                  # Set directly
nav.set_page_title_from_model_name(models.Task)         # verbose_name
nav.set_page_title_from_model_plural_name(models.Task)  # verbose_name_plural
nav.set_page_title_to_form_action_from_model_instance(task)

nav.breadcrumbs.add('Home', href='/')                     # or view_name='...'
nav.breadcrumbs.add('Details', view_name='task:page:detail', view_kwargs={'pk': task.pk})
nav.breadcrumbs.add_model_name(models.Task)              # verbose_name
nav.breadcrumbs.add_model_plural_name(models.Task)       # verbose_name_plural
nav.breadcrumbs.add_model_instance_string(task)          # str(task)

context = nav.as_context()
```

## Forms

### Confirmation Forms

Both forms require an `obj` and expose `save(user, verbs, ...)`:

```python
from django_spire.contrib.form.confirmation_forms import (
    ConfirmationForm,
    DeleteConfirmationForm,
)

form = DeleteConfirmationForm(request.POST or None, obj=task)

if form.is_valid():
    form.save(
        user=request.user,
        verbs=('delete', 'deleted'),
        delete_func=task.set_deleted,       # Optional; defaults to obj.set_deleted()
        activity_func=None,                  # Optional custom activity
        auto_add_activity=True,              # Adds activity unless activity_func given
    )
```

`ConfirmationForm` is the same with `confirmation_func` instead of `delete_func`.

## Test Base

```python
from django_spire.core.tests.test_cases import BaseTestCase

class MyTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()  # Creates super_user, force_login to self.client
```

## Seeding

Define seeders for test data (`Seeder` with a `fields_seeds` dict):

```python
from django_spire.contrib.seeding import Seeder

class TaskModelSeeder(Seeder):
    model_class = Task

    fields_seeds = {
        'id': Seeder.exclude(),
        'attachment': Seeder.file(),
        'parent_id': Seeder.model.random_foreign_key(Task),
        'name': Seeder.fake.sentence(),
        'description': Seeder.fake.paragraph(3),
        'status': Seeder.model.random_field_choice(TaskStatusChoices),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }
```

Key methods: `seed()`, `seed_database()`, `reseed_database()`, `to_list_of_dicts()`, `to_model_instances()`, `seed_class()`, `queryset`, `meta`, and `Seeder.print_meta_overview()`.

### Field Seeders

| Helper | Example |
|--------|---------|
| `Seeder.fake.<faker>` | `Seeder.fake.sentence()`, `Seeder.fake.paragraph(3)`, `Seeder.fake.date_time_between(...)` |
| `Seeder.model.random_foreign_key(Model)` | Random FK to any instance of a model |
| `Seeder.model.random_queryset_foreign_key(qs)` | Random FK filtered by a queryset |
| `Seeder.model.ordered_foreign_key(Model)` / `ordered_queryset_foreign_key(qs)` | Sequential FKs |
| `Seeder.model.random_field_choice(Choices)` | Random choice from a TextChoices/Choices |
| `Seeder.random.choice(seq)` / `int(a, b)` / `float(a, b)` | Random values |
| `Seeder.static(value)` | Static values |
| `Seeder.exclude()` | Skip a field |
| `Seeder.file(upload_to=None)` | File upload |
| `Seeder.llm(field_type, prompt=None, locale='en_CA')` | AI-generated |
| `Seeder.index(index_start=0, index_step=1)` | Sequential index |
| `Seeder.custom.callable(fn, ...)` | Custom callable |
| `Seeder.mutate.corrupt(...)` / `exclude(...)` / `nullable(...)` / `type(...)` / `value(...)` | Mutations for corrupt/nullable data |

## Contrib Packages

| Package | Purpose | Key Files |
|---------|---------|-----------|
| `admin` | Admin utilities | `options/mixins.py` |
| `constants` | Constants | |
| `constructor` | Model construction & services | `service/django_model_service.py` |
| `converters` | Type/data converters | `to_pydantic.py` |
| `form` | Form utilities | `confirmation_forms.py`, `widgets.py`, `tools.py` |
| `maps` | Lookup maps | `maps.py` |
| `navigation` | Breadcrumbs & navigation | `navigation.py`, `breadcrumbs.py` |
| `options` | Admin/field options | `mixins.py` |
| `ordering` | Sort ordering | `mixins.py`, `services/` |
| `redirects` | Safe redirect helpers | `redirects.py` |
| `responses` | JSON responses | `json_response.py` |
| `rest` | REST utilities | `connector/`, `schema/` |
| `seeding` | Test data | `seeder.py`, `field/` |
| `session` | Session controller | `templatetags/session_tags.py` |
| `shortcuts` | View/model shortcuts | `shortcuts.py` |
| `utils` | Misc utilities | `utils.py` |

## Settings

| File | Purpose |
|------|---------|
| `base_settings.py` | Base configuration, loads `development.env` |
| `postgres_settings.py` | PostgreSQL database config |
| `test_settings.py` | pytest config, `TEST_DATABASE_*` env vars (port 5439 default) |
| `dandy_settings.py` | Dandy-specific config |
| `sqlite_settings.py` | SQLite config |
| `django_spire/settings.py` | `DJANGO_SPIRE_*` default settings |
| `django_spire/conf.py` | `settings` wrapper (project + default values, merges `DJANGO_SPIRE_AUTH_CONTROLLERS`) |

Common `DJANGO_SPIRE_*` settings (defaults in `django_spire/settings.py`): `DJANGO_SPIRE_AUTH_CONTROLLERS`, `DJANGO_SPIRE_NAVIGATION_HOME_URL`, `DJANGO_SPIRE_DEFAULT_THEME_MODE`, `DJANGO_SPIRE_AI_PERSONA_NAME`, `DJANGO_SPIRE_NOTIFICATION_THROTTLE_RATE_PER_MINUTE`, `DJANGO_SPIRE_CHANGELOG_MODULE`, `DJANGO_SPIRE_REPORT_REGISTRIES`.

## Environment

- `development.env` - Local defaults (database, AWS, AI APIs, Twilio, Celery, SendGrid)
- Loaded by `base_settings.py` via `python-dotenv` (and `justfile` via `dotenv-load`)
- `DJANGO_SETTINGS_MODULE` - Points to active settings module (`test_project.postgres_settings` for local server)
- `DANDY_SETTINGS_MODULE` - Dandy config used alongside Django settings
- `TEST_DATABASE_*` - Override test DB (name/user/password/host/port, 5439 default)

## Frontend Libraries

The JS libraries are CDN-hosted or vendored in the base template (`django_spire/core/templates/django_spire/base/base.html`). Core Spire JS globals (`Spire`, plus `ajax`, `modal`, `notify`, `cookie`, `session`, `date`, `theme`, `ui`, `full-screen`, `pull-to-refresh`, `activity`) are served from `django_spire/core/static/django_spire/js/`.

### Alpine.js (Primary JS Framework)

Alpine.js is the primary frontend framework for reactivity. Plugins are loaded as defer scripts (3.15.x):

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/intersect@3.15.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/mask@3.15.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/collapse@3.15.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.15.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.15.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/sort@3.15.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.x/dist/cdn.min.js"></script>
```

### Django Glue Integration

`django_glue` provides server-side data binding with Alpine.js. Glue objects are created in views:

```python
from django_glue import Glue

Glue.model(request, 'task', task, Glue.Access.CHANGE, fields=[...], form_class=forms.TaskModelForm)
Glue.queryset(request, 'tasks', tasks, Glue.Access.CHANGE, fields=[...], form=forms.TaskModelForm())
Glue.form(request, 'task_form', form, Glue.Access.CHANGE)
```

`Glue.Access`: `VIEW`, `CHANGE`, `DELETE` (cascade). In the base template call `{% load django_glue %}` + `{% django_glue_init %}`. Client-side, bound objects are exposed on the `Glue` global (e.g. `Glue.querySet.tasks`, `Glue.model.task.form`) and consumed by Alpine. Template tags: `{% django_glue_init %}`, `{% js_url 'task:page:detail' pk='item.id' %}`, plus filters `glue_field_value_path` / `glue_field_metadata_path`.

### Bootstrap 5.3

```html
<link rel="stylesheet" href="{% static 'django_spire/css/django-spire-bootstrap.css' %}">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.x/dist/js/bootstrap.bundle.min.js"></script>
```

CSS is compiled locally from SCSS (not a CDN link). Bootstrap JS stays on the CDN. Custom overrides/extensions live in the SCSS (`_bootstrap_overrides.scss`, `_bootstrap_extensions.scss`).

### Bootstrap Icons

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.x/font/bootstrap-icons.min.css">
```

### Flatpickr

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
```

### ECharts

```html
<script defer src="https://cdn.jsdelivr.net/npm/echarts@5.4.x/dist/echarts.min.js"></script>
```

### Axios

```html
<script defer src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
```

### Pulltorefresh.js

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/pulltorefreshjs/0.1.22/index.umd.min.js"></script>
```

### Theme System

Themes are cookie-driven with light/dark modes. The base template sets the theme mode:

```html
<html lang="en" data-bs-theme="{{ DJANGO_SPIRE_THEME_MODE }}">
```

- Mode is stored in cookie `django_spire-theme-mode`; default from `DJANGO_SPIRE_DEFAULT_THEME_MODE` (`'light'`)
- Theme behavior is in `django_spire/core/static/django_spire/js/theme.js`; styles come from SCSS `_theme.scss` variables
- Colors/styles belong in SCSS, not templates (see ZEN.md)

### SCSS

SCSS is compiled via a Django management command (uses the `libsass` Python package), not a JS toolchain:

```bash
just scss   # python manage.py spire_compile_scss
```

- Framework SCSS source: `django_spire/core/static/django_spire/scss/` (includes vendored `bootstrap/`)
- Project overrides/theme: `<static>/django_spire/scss/_theme.scss` (e.g. `test_project/static_files/django_spire/scss/`)
- Entry point: `_theme.scss`; output: `<static>/django_spire/css/django-spire-bootstrap.css`
- Add new Bootstrap versions by updating the vendored `bootstrap/` sources

## Reference Examples

| Pattern | Location |
|---------|----------|
| Full app | `test_project/app/task/` |
| Service layer | `test_project/app/model_and_service/` |
| Navigation/breadcrumbs | `test_project/app/task/navigation.py` |
| Views (page/form/modal) | `test_project/app/task/views/` |
| Seeding | `test_project/app/task/seeding/seeder.py` |
| API core | `django_spire/api/api_v1.py` |
| URLs | `django_spire/urls.py` |
| Choices | `django_spire/help_desk/choices.py` |
| Auth controller | `django_spire/help_desk/auth/controller.py` |
