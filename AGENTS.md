# Agent Guidelines

- Always use `just` for running commands (loads `development.env`)
- Run `just` to see all available commands
- Do not comment code - write it so it doesn't need comments
- Pull **current** project facts from the tools, not the reference lists below (which can drift): the constellation graph for code structure, `justfile` for commands, `pyproject.toml`/pytest for test config, and `django_spire/core/templates/django_spire/base/base.html` for frontend libraries.

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
just test                    # pytest . --reuse-db (-n 12, excludes ai, playwright & e2e)
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
- Markers: `ai`, `demo`, `e2e`, `playwright`, `simulation`, `slow`, `postgres_only`
- Default addopts in `pyproject.toml`: `-v --tb=short -n 12 --ds=test_project.test_settings -m 'not ai and not playwright and not e2e'` (AI, Playwright, and browser e2e tests are excluded by default)
- `just test*` recipes add `--reuse-db`
- Browser end-to-end tests (Playwright / limelight) are marked `e2e` (usually alongside `playwright`/`demo`) so the default run and CI skip them — they need a real browser. Run them explicitly with `pytest -m e2e` after `playwright install`.
- Playwright tests may also live under `test_playwright/` directories (skipped by `norecursedirs`); run config in `test_project/playwright.config.py`, reusable fixtures/pages/components in `django_spire/testing/playwright/`
- CI (`.github/workflows/ci.yml`): boots Postgres via `test_project/docker-compose.test.yml`, runs pytest; the `e2e` marker exclusion (via addopts) keeps browser tests out of that job

## Code Quality

- **Linter**: `ruff` (config in `ruff.toml`) - `select = ["ALL"]` with ignores (docstrings `D*`, `C901` complexity, etc.), max complexity 6
- **Format**: `ruff format` - single quotes, 100 char lines, 4 space indent
- **Type checker**: `pyrefly` is available (dev extra) with config in `ty.toml` (`invalid-argument-type` = warn). Not wired into `just` or CI - run it manually if you want type checking.
- **CI order**: linting → tests → security (lint must pass first)

## Architecture

Two top-level packages:

- `django_spire/` — the framework package (published to PyPI). Apps (`ai`, `api`, `auth`, `celery`, `comment`, `core`, `file`, `help_desk`, `history`, `knowledge`, `metric`, `notification`) follow the App Pattern below. `django_spire/urls.py` auto-discovers each app's `URLPATTERNS_INCLUDE`. `metric` is a single app with an internal `domain`/`visual`/`report` structure rather than one app per concern.
- `test_project/` — the test/demo Django project: settings modules (`base_settings`, `postgres_settings`, `sqlite_settings`, `test_settings`, `dandy_settings`), `seed.py`, process entry points, and example apps under `test_project/app/`.

For the live layout and Django surface, use the constellation tools (`files`, `overview`, `routes`) instead of trusting this summary as exhaustive.

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

`URLPATTERNS_INCLUDE` + `URLPATTERNS_NAMESPACE` are auto-discovered by `django_spire/urls.py`. Other management commands: `spire_flush` (wipe DB + reseed), `spire_remove_migration <app>` (delete a migration), and `metric/domain/... prune_metric_statistic_values` (cleanup old metric values).

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

Activity records are created automatically. `ActivityUserMiddleware` stores the
request user in a context variable, and `post_save`/`post_delete` signal
receivers (connected per `ActivityMixin` model at app startup, so other models
keep Django's fast-delete path) create a `created`/`updated`/`deleted` activity
for any `ActivityMixin` model saved or deleted during the request.
`set_deleted()` logs `deleted`, not `updated`; `update(is_deleted=True)` and
`bulk_update` with `is_deleted` in its fields do the same for rows that were
not already deleted, so soft deletes carry the `deleted` verb on every path.
The automatic verbs come from the `ActivityVerb` enum
(`django_spire/history/activity/enums.py`); `Activity.verb` stays a plain
`CharField` because `add_activity` accepts custom verbs. Bulk operations are
covered when the model's default manager derives from `HistoryQuerySet`:
`bulk_create`, `bulk_update`, `update`, and `delete` bulk-insert activities,
capped at `BULK_ACTIVITY_COUNT_MAX` rows per call with a logged warning on
truncation (`bulk_create(ignore_conflicts=True)` cannot recover primary keys,
and `bulk_create(update_conflicts=True)` cannot distinguish created rows from
updated rows, so each logs a warning instead of activities). Each bulk
operation wraps the write and its activity insert in one transaction, so a
failed audit insert rolls the write back rather than leaving unaudited rows;
a bulk delete that removes the acting user's own row skips its activity
records with a logged warning instead of violating the `Activity.user`
foreign key. `update()` snapshots target primary keys without locking, so
under concurrent writes the audit can include rows the update did not modify;
it logs a warning when the updated row count falls short of the snapshot. An
`m2m_changed` receiver logs `added`/`removed` activities for `add`, `remove`,
`clear`, and `set` on `ActivityMixin` instances, counting only rows actually
added or removed and naming up to `ACTIVITY_M2M_NAMED_COUNT_MAX` affected
rows in the information text, with an `and N more` suffix beyond the cap. The
activity attaches to the instance whose manager is called, so mutate a
relation from the side whose log matters: `group.user_set.remove(user)` logs
on the group, `user.groups.remove(group)` logs on the user, and nothing is
logged when that side is not an `ActivityMixin` model. Self-referential m2m
fields log from both sides; the signal's `reverse` flag resolves which
through column is the source when both columns point at the same model.
Two cascade behaviors are not logged: `on_delete=SET_NULL`/`SET_DEFAULT`
nulls the child column through the delete collector's raw UPDATE, which
bypasses querysets and signals, so only the parent's `deleted` activity
records the change; and deleting a multi-table-inheritance child logs
`deleted` once per table row, so an MTI model produces two entries for one
logical object.
Outside a request (Celery tasks, management commands, cron) no user is in
context and nothing is logged; wrap the work in
`django_spire.history.activity.context.activity_user(user)` at the entry
point to attribute it. That entry-point wrap is the ONLY manual step the
system has: attribution is automatic everywhere else, so services must not
take a `user` argument for activity purposes, must not wrap their saves in
`activity_user(...)`, and callers must not pass a user for attribution. A
`user` parameter on a service is legitimate only when it is real field data
(for example `HelpDeskTicketService` setting `created_by`).
Hard-deleting an instance cascades its existing activity rows (the
`GenericRelation` on `ActivityMixin`); only the final `deleted` activity
survives as a tombstone, so soft delete is the path that preserves history.
Do not call `add_activity` for those verbs in views or services; call it
directly only for custom verbs or when a recipient/subscribers are needed.
System checks cover the two silent failure modes:
`django_spire_history_activity.W001`/`W002` warn when the middleware is
missing or misordered, and `W003` warns when an `ActivityMixin` model's
default manager does not use a `HistoryQuerySet`, because instance saves
would still log while bulk operations silently would not. The middleware must
be listed in `MIDDLEWARE` after `AuthenticationMiddleware`:

```python
MIDDLEWARE = [
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_spire.history.activity.middleware.ActivityUserMiddleware',
    ...
]
```

See `django_spire/history/activity/mixins.py`, `signals.py`, and `middleware.py`.

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

## Search Palette

`django_spire/core/search/` powers the Ctrl/Cmd-K search palette. Apps register a `Search` subclass per model in `DJANGO_SPIRE_SEARCH_REGISTRY` (dict of `search_key` → module string, e.g. `'TASK': 'test_project.app.task.search.TaskSearch'` in `base_settings.py`). Adds an `icon`/`action` entry in the nav automatically via the registry - no URL wiring needed.

```python
from django_spire.core.search import Search

class TaskSearch(Search):
    model_class = models.Task
    searchable_fields = ['name', 'description']   # OR'd per whitespace-separated word
    search_key = 'TASK'                            # REQUIRED, must match registry key
    name = 'Tasks'
    icon = 'bi-list-task'
    permission = 'test_project_task.add_task'      # Optional

    searchable_commands = [
        Search.Command(
            name='New Task',
            icon='bi-plus-lg',
            url=reverse('task:modal:form', kwargs={'pk': 0}),
            action=Search.Command.Action.DISPATCH_MODAL,
            description='Create a new task',
            permission='test_project_task.add_task',
        )
    ]

    def base_queryset(self, request: HttpRequest) -> QuerySet: ...      # REQUIRED
    def generate_list_url(self) -> str: ...                              # REQUIRED
    def generate_detail_url(self, obj) -> str: ...                       # REQUIRED
    def result_name(self, obj) -> str: ...                               # REQUIRED
    def result_description(self, obj) -> str | None: ...                 # REQUIRED
```

Required attributes (`model_class`, `searchable_fields`, `search_key`) raise `ValueError` in `__init_subclass__` if unset. `search_key` must match the registry key or the registry raises `ValueError`. Reference implementations: `django_spire/knowledge/entry/search.py` (`EntrySearch`) and `test_project/app/task/search.py` (`TaskSearch`). Registry logic in `core/search/registry.py`, palette view in `core/search/views.py`, client JS in `core/static/django_spire/js/search_palette.js`.

## Access Control

Guard views with the permission decorator (redirects anonymous users to login, raises `PermissionDenied` otherwise; supports `all_required=False`):

```python
from django_spire.auth.permissions.decorators import permission_required

@permission_required('django_spire_app.view_model')
def model_list_view(request):
    ...
```

Use Django's built-in `perms` context variable in templates:

```html
{% if perms.django_spire_app.add_model %}
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

Delete view (soft delete; the save signal logs a `deleted` activity when
`set_deleted()` flips the flag):

```python
@login_required()
def delete_view(request, pk):
    task = get_object_or_404(models.Task, pk=pk)
    return_url = request.GET.get('return_url', reverse('task:page:list'))

    if request.method == 'POST':
        task.set_deleted()
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
               fields=['name', 'description', 'status'], form=forms.TaskModelForm)

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

Both forms require an `obj` and expose `save(user, ...)`:

```python
from django_spire.contrib.form.confirmation_forms import (
    ConfirmationForm,
    DeleteConfirmationForm,
)

form = DeleteConfirmationForm(request.POST or None, obj=task)

if form.is_valid():
    form.save(
        user=request.user,
        delete_func=task.set_deleted,       # Optional; defaults to obj.set_deleted()
    )
```

`ConfirmationForm` is the same with `confirmation_func` instead of `delete_func`.
Activity records come from the activity signals, not from these forms. The
legacy `verbs` and `auto_add_activity` arguments are accepted for backwards
compatibility but ignored with a `DeprecationWarning`; `activity_func` is
still invoked for its side effects, also with a `DeprecationWarning`.

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
| `Seeder.model.ordered_foreign_key(Model)` / `ordered_queryset_foreign_key(qs)` | Sequential FKs (`wrap=True` cycles instead of erroring past the FK count) |
| `Seeder.model.ordered_field_choice(Choices)` | Rotates through a TextChoices/Choices in declared order |
| `Seeder.model.random_field_choice(Choices)` | Random choice from a TextChoices/Choices |
| `Seeder.random.choice(seq)` / `int(a, b)` / `float(a, b)` | Random values |
| `Seeder.ordered.choice(seq)` | Rotates through a custom list of values (`wrap=True` to cycle, default raises out of range) |
| `Seeder.ordered.datetime(start, step)` | Ascending datetime per seed (`start` + `seed_index * step`) |
| `Seeder.static(value)` | Static values |
| `Seeder.exclude()` | Skip a field |
| `Seeder.file(upload_to=None)` | File upload |
| `Seeder.llm(field_type, prompt=None, locale='en_CA')` | AI-generated |
| `Seeder.index(index_start=0, index_step=1)` | Sequential index |
| `Seeder.custom.callable(fn, ...)` | Custom callable |
| `Seeder.mutate.corrupt(...)` / `exclude(...)` / `nullable(...)` / `type(...)` / `value(...)` | Mutations for corrupt/nullable data |

## Contrib Packages

Reusable utilities under `django_spire/contrib/`. The most-used for building: `constructor` (services), `form` (`confirmation_forms.py`, `widgets.py`), `navigation` (`navigation.py`, `breadcrumbs.py`), `seeding` (`seeder.py`), `shortcuts` (`get_object_or_null_obj`), `redirects` (`safe_redirect_url`), `responses` (`json_response.py`), `rest` (`connector/`, `schema/`).

For the full, current list use `constellation files contrib/` (or `ls django_spire/contrib/`) — it changes; don't trust this list as exhaustive.

## Settings

| File | Purpose |
|------|---------|
| `base_settings.py` | Base configuration, loads `development.env` |
| `postgres_settings.py` | PostgreSQL database config |
| `test_settings.py` | pytest config, `TEST_DATABASE_*` env vars (port 5439 default) |
| `dandy_settings.py` | Dandy-specific config |
| `sqlite_settings.py` | SQLite config |
| `django_spire/settings.py` | `DJANGO_SPIRE_*` default settings |
| `django_spire/conf.py` | `settings` wrapper (project + default values) |

Common `DJANGO_SPIRE_*` settings (defaults in `django_spire/settings.py`): `DJANGO_SPIRE_NAVIGATION_HOME_URL`, `DJANGO_SPIRE_DEFAULT_THEME_MODE`, `DJANGO_SPIRE_AI_PERSONA_NAME`, `DJANGO_SPIRE_NOTIFICATION_THROTTLE_RATE_PER_MINUTE`, `DJANGO_SPIRE_CHANGELOG_MODULE`, `DJANGO_SPIRE_REPORT_REGISTRIES`, `DJANGO_SPIRE_SEARCH_REGISTRY` (search palette class mapping), and a metric/remote group (`DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX`, `DJANGO_SPIRE_METRIC_RETENTION_DAYS`, `DJANGO_SPIRE_METRIC_VISUAL_REGIONS`, `DJANGO_SPIRE_INTERNAL_METRIC_*`, `DJANGO_SPIRE_REMOTE_API_URL`/`KEY`).

## Environment

- `development.env` - Local defaults (database, AWS, AI APIs, Twilio, Celery, SendGrid)
- Loaded by `base_settings.py` via `python-dotenv` (and `justfile` via `dotenv-load`)
- `DJANGO_SETTINGS_MODULE` - Points to active settings module (`test_project.postgres_settings` for local server)
- `DANDY_SETTINGS_MODULE` - Dandy config used alongside Django settings
- `TEST_DATABASE_*` - Override test DB (name/user/password/host/port, 5439 default)

## Frontend

`django_spire/core/templates/django_spire/base/base.html` is the source of truth for loaded libraries and versions (read it rather than pinning CDN URLs by hand). Core Spire JS globals (`Spire`, `ajax`, `modal`, `notify`, `cookie`, `session`, `date`, `theme`, `ui`, `full-screen`, `pull-to-refresh`, `activity`) live in `django_spire/core/static/django_spire/js/`.

- **Alpine.js** is the primary reactivity framework; plugins (`@alpinejs/*`) are loaded as defer scripts from CDN in `base.html`.
- **django_glue** (`Glue.model` / `Glue.queryset` / `Glue.form` with `Glue.Access` VIEW/CHANGE/DELETE) binds server state to Alpine. In `base.html`: `{% load django_glue %}` + `{% django_glue_init %}`; client-side objects are exposed on the `Glue` global (e.g. `Glue.querySet.tasks`).
- **Bootstrap 5** CSS is compiled locally from SCSS (`just scss`, sources in `django_spire/core/static/django_spire/scss/`); Bootstrap JS and Bootstrap Icons load from CDN.
- **Flatpickr, ECharts, Axios, pulltorefresh.js** load from CDN (see `base.html`).
- **Theme**: cookie-driven, `light`/`dark` (`DJANGO_SPIRE_THEME_MODE`); colors/styles belong in SCSS (`_theme.scss`), not templates (see `docs/getting_started/zen.md`).

## Constellation Code Intelligence (MCP)

A pre-built cross-project knowledge graph of these Django codebases is served to the agent over MCP (`~/.config/opencode/opencode.jsonc` → `mcp.constellation`; `constellation serve --supervise`). Consult it **before** reaching for Grep/Read on any code-intelligence question (where a symbol lives, how it works, what calls/render/extends/relates to what, a model's effective schema, or the blast radius of a change). The graph resolves Django structure grep cannot: routes↔views, views↔templates (render/module kwargs), template extends/includes, model fields and foreign keys, return/attribute types, signal handlers, and third-party base/mixin inheritance.

The tools are live only for indexed repos (a `.constellation/index.db`). If a tool reports "no constellation index for this working directory", index this repo first:

```bash
constellation init                       # create and index .constellation/index.db here
constellation link <db> <repo>...        # link multiple repos into one graph (companions: django-glue, dandy, robit)
constellation sync                       # re-index every project and re-link
constellation flows                      # trace and rank Django execution flows (used by flows/affected_flows)
constellation history [--symbols]        # ingest git history (used by history/symbol_history/as_of)
```

### Key tools (by intent)

| Tool | Purpose |
|------|---------|
| `explore` | PRIMARY, try first. Give one or two rare identifiers (e.g. `ArticleForm subtotal_amount`) and get relevant source grouped by file; name two symbols to trace the call path between them. `outline=true` for a signal-only survey. |
| `overview` | Orient first when unfamiliar: per-project file/symbol counts, Django surface, largest packages, cross-project link total. |
| `search` | Find a symbol by name (substring/fuzzy); returns locations only. |
| `node` | One symbol: kind, signature, docstring, caller/callee counts. |
| `model` | A Django model's effective schema (own + inherited fields, bases, relations) in one call. |
| `callers` / `callees` | What references a symbol / what it references, including Django edges grep can't follow. |
| `impact` | Transitive non-test callers (blast radius) before a change. |
| `path` | Shortest call/flow path between two symbols. |
| `at` | The symbol at a file:line (map a traceback frame or grep hit to its enclosing function). |
| `files` | Project layout / package breakdown; faster than globbing. |
| `flows` | Every Django execution flow ranked by criticality (needs `constellation flows`). |
| `affected_flows` | Which user-facing flows a diff touches, ranked by criticality. |
| `changed` | Symbols overlapping the working-tree diff, risk-ranked with a 0.00–1.00 score. |
| `feature` | Vertical slice: route→view→template(s), model relations, services, signals as one digest. |
| `tests` | Tests covering a symbol (or `(no covering tests)`). |
| `subclasses` | Transitive subclasses of a base/mixin. |
| `winnow` | Compose criteria (kind, relates_to, changed_since, tested, risk, ...) into one ANDed query. |
| `status` | Index health and working-tree staleness. |
| `history` / `symbol_history` / `as_of` | File/symbol change over time, or reconstruct the codebase as of a commit/date (needs `constellation history [--symbols]`). |
| `links` / `orphans` | Cross-project import links / candidate dead code. |
| `routes` | Full URL map: pattern → view → template. |

### Caveats

- Indexes are scoped to imports; some layers are known-dark (chained queryset methods, function-local imports, template/`__str__`/admin-only reach, string-reference FKs) — a low caller/impact count there is NOT "safe to change"; verify before deleting.
- If a tool "requires X to have been run" (flows/history/symbol_history), run the corresponding `constellation` subcommand to populate that index.

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
