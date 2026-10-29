# Changelog

## v1.4.1

### Fixed

- `metric_build --registry` no longer flags rows declared by other registered
  registries as orphaned; the orphan pass now runs only on a full build.
- `metric_build` no longer crashes when a `REMOTE`-targeted registry is
  registered: build mode skips each one with a printed line, and `--check`
  still probes it. A remote registry's keys are not counted as declared for
  the orphan pass, since they describe rows on the target installation.
- `JsonTreeWidget` no longer crashes on a JSON object with a key named
  `items`: the tree template's `dict.items` resolved to that key's value
  before the dict's `.items()` method, so the key/value loop tried to unpack
  it. The tree now iterates an explicit `dict_items` filter.

### Docs

- The v1.4.0 entry said the API `MetricKey` pattern "no longer accepts
  underscores or `--`". It accepts `--`, because the API takes the stored key
  form; the v1.4.0 entry is corrected.

## v1.4.0 - October 27, 2026

### Breaking

- `FormComponent` and `ModelFormComponent` are reworked. A subclass written for 1.3
  updates these names:
  - `form` is renamed `form_class`.
  - `attr` is removed. The child is always `form` on a `FormComponent` and `model` on a
    `ModelFormComponent`, so a template that reached it by a custom name, such as
    `modal.time_entry.form`, reads `modal.model.form`. Templates that use
    `component.glue_form_path` need no change.
  - `ModelFormComponent.model_class` is removed; the model is the form's own. `fields` is
    optional and defaults to the form's fields.
  - `build_child()` is removed. Override `get_form()`, or the hooks on
    `ModelFormComponent`, instead.
  - `ModelFormComponent` no longer inherits from `FormComponent`. Both inherit from the new
    `BaseFormComponent`.
- The components moved from `django_spire.core.glue.components` to
  `django_spire.core.components`, with no alias at the old path. Import every component
  from there: `from django_spire.core.components import ModelFormComponent`.
- `django_spire/js/search_palette.js` moved to `django_spire/js/components/search_palette.js`,
  beside the other scripts that register an Alpine component. Spire's `base.html` loads it
  from there; a project that loads it by path updates the path.
- The metric stored-key separator changes from `__` to `--`
  (`store--web`, `store--orders--created`); the migration
  `0012_metric_key_object_separator` rewrites the existing rows in the four metric tables.
  Metric spec keys are strict lowercase slugs (underscores are rejected), the API
  `MetricKey` pattern no longer accepts underscores (it accepts `--`, because the
  API takes the stored key form), and the click-tracking settings
  `DJANGO_SPIRE_METRIC_STATISTIC_KEY` and `DJANGO_SPIRE_METRIC_SUB_DOMAIN_KEY`
  must use the stored key form.
- `BaseReport.add_column()`'s `type` argument is renamed `column_type`. Positional
  calls are unaffected; a report that passes `type=` by keyword raises `TypeError`
  until the name is updated.
- The `password_reset_key_form`, `password_reset_key_form_done` and `password_set_form`
  URLs in `django_spire:auth:admin:` are removed, with their views and their
  `password_reset_key_form_page.html`, `password_reset_key_done_page.html` and
  `password_set_form_page.html` templates. Nothing linked to them, and their pages linked
  to URLs Spire does not have. The password reset flow is unchanged.

### Added

- Scroll components, in `django_spire.core.components`, for infinite lists
  built as Glue components. The template scroll in `django_spire/glue/scroll/` is unchanged
  (ADR 0002):
  - `BaseScrollComponent` lists items of any kind. A subclass writes
    `get_items(offset, limit)`, `get_item(key)` and `get_item_key(item)`.
    `item_template` is the markup for one row, rendered on the server. Controls are
    editable attributes the subclass declares, and the template's `reloadItems()` applies
    them.
  - `QuerySetScrollComponent` lists the rows of `get_queryset()`, by primary key when it has
    no ordering. `get_instance(pk)` returns one row of that queryset for a callable that
    acts on it, and reports a row outside the list as a 404.
  - `glue_items = True` on a queryset scroll sends each row as the Glue model its
    `get_glue_item(item, name)` builds, drawn in the browser in the template's `scroll_item`
    block, so row markup can call the model's Glue methods and services and save its fields.
    The browser loads these rows with the `load_glue_items` and `load_glue_item` callables.
  - `ModelCrudScrollComponent` adds create, edit and delete, configured with option
    classes it carries as attributes. `item_form_options` is a
    `ModelCrudScrollComponent.FormOptions`, which shows a form component in a modal, or a
    `ModelCrudScrollComponent.PageFormOptions`, which sends the user to a page.
    `item_delete_options` is a `ModelCrudScrollComponent.DeleteOptions`, which shows a
    confirmation component in a modal and soft-deletes by default, or a
    `ModelCrudScrollComponent.PageDeleteOptions`, which sends the user to a delete page.
    The classes are defined in the form and confirmation packages. A page link carries a `return_url`: the route named by the options'
    `return_url_name`, or the address the list is shown at. The template gains
    `createItem()`, `editItem(item)` and `deleteItem(item)`. The browser fetches the modal
    components with the `load_item_form` and `load_item_delete_confirmation` callables,
    which check the user's access and that the row is in the list.
  - One row is updated at a time with the template's `addItem(key)`, `refreshItem(key)` and
    `removeItem(key)`, or by firing `item_added`, `item_changed` or `item_removed` from a
    callable.
  - Templates are `django_spire/component/scroll/scroll.html`, `table_scroll.html` and
    `crud_scroll.html`, with `item/item.html` and `item/table_item.html` for
    server-rendered rows.
  - The client behaviour is the `scrollComponent` and `crudScrollComponent` Alpine
    components in `django_spire/js/components/scroll.js`, which Spire's `base.html` loads.
- `django_spire/button/async_button.html`, a button that runs one awaited call and is off,
  showing a spinner, until it settles. It takes `x_button_click`, `button_text`,
  `button_class`, `button_icon` and `button_title`. Buttons given the same `x_busy` flag
  take turns. The behaviour is `asyncButton` in
  `django_spire/js/components/async_button.js`, which any element can use directly with
  one attribute: `x-bind="asyncButton(() => component.save())"`.
- A project that does not extend Spire's `base.html` must load the scripts in
  `django_spire/js/components/` itself.
- Confirmation components, in `django_spire.core.components`.
  `BaseConfirmationComponent` asks the user to confirm one action and fires `confirmed` or
  `cancelled`. Its prompt is worded with `title`, `message` and `confirm_label` when it is
  built. Cancelling makes no request: the template raises `cancelled` in the browser with
  Glue's `$dispatch`, which needs `django-glue` 1.3.0.
  - `BaseModelActionConfirmationComponent` confirms one action on one model row, built as
    `(instance=row)`. A subclass writes `perform_action()`, and `confirmed` carries the
    row's `pk`.
  - `BaseModelDeleteConfirmationComponent` words that as a delete and requires `DELETE`
    access. `ModelSetDeletedConfirmationComponent` soft-deletes the row with
    `set_deleted()`, and `ModelDeleteConfirmationComponent` deletes it from the database.
    Both work for any model with no subclass.
- `ScrollComponent`, a Playwright helper in `django_spire.testing.playwright` for the new
  scroll.
- `django_spire/component/page/full_page.html`, a full page whose content is one Glue
  component. A component served as a page names it as its `view_template`.
- A form component can be built without a subclass:
  `ModelFormComponent(form_class=TaskForm, template='task/form.html', pk=pk)`. The form
  class must be defined at module level.
- The metric registry, a declarative way to declare and sync the metric structure
  (domains, sub-domains, statistic groups, and statistics) in code instead of the admin.
  - `Metric` (in `django_spire.metric.metric`) declares the structure with nested spec
    constructors: a subclass sets `domains` to a list of `Metric.Domain` specs, each
    holding `Metric.SubDomain` and `Metric.StatisticGroup` specs, and each group holding
    `Metric.Statistic` specs. The first argument of every constructor is the **key**, a
    lowercase slug, and the remaining fields mirror the model fields (`name`,
    `description`, `sub_domain_name`, `interval`, `value_type`).
  - The registry is registered in settings: `DJANGO_SPIRE_METRIC_REGISTRY` is a list of
    dotted paths to `Metric` subclasses (default `[]`).
  - Specs are validated when the class is defined: a `target` that is not a
    `Metric.Target`, a non-spec entry, empty `domains`, a non-slug key, `--` in a key,
    duplicate keys, an unknown `interval` or `value_type`, and a stored key over
    64 characters all raise immediately.
  - `Domain` and `StatisticGroup` gain a unique `key` field, backfilled from the name for
    existing rows. Stored keys are namespaced by their parents, joined with `--` as the
    object separator (`store--web`, `store--orders--created`), so the same local key can
    be reused under different domains. Renaming a spec's **name** is safe; changing a
    **key** after values have been recorded gives the row a new key and orphans the old
    one.
  - `Metric.build()` syncs the structure into the database: it find-or-creates every
    level by key, updates `name`, `description`, `sub_domain_name`, `interval` and
    `value_type` when they drifted from the spec, never touches `is_active` or
    `is_deleted`, and reports a soft-deleted row as an error instead of resurrecting it.
  - `Metric.check()` performs the same walk without writing: a row whose fields drifted
    from the spec is reported as an error, so a drifted structure fails the check. For a
    `REMOTE` target it probes the remote installation's API, and a probe that fails — an
    HTTP error or a network error — is counted as missing, so a downed remote reports as
    drift instead of crashing the check.
  - `Metric.record(domain_key, sub_domain_key, statistic_group_key, statistic_key,
    reference, value=1, *, source_model=None)` writes a value. It validates the keys
    against the declared spec synchronously (an unknown key or sub-domain raises
    `ValueError`), then dispatches the write to a bounded worker pool (sized by
    `DJANGO_SPIRE_METRIC_RECORD_WORKERS`, default 2) and returns a handle whose
    `join()` waits for the write, so a record never blocks the caller or raises: a failed
    write is logged and dropped, and the worker closes its own database connections when
    the task finishes. `reference` is required and must be a list of strings — a bare
    string is rejected with `TypeError` — and the segments are joined with `:` for
    storage. A saved Django model instance passed as `source_model` appends
    `<app_label>.<model_name>:<pk>` to the stored reference, so `['order', 'created']`
    plus a task with pk 7 stores `order:created:myapp.task:7`.
  - A registry targets `Metric.Target.LOCAL` (the default), which stores `StatisticValue`
    rows in this database, or `Metric.Target.REMOTE` with a `remote_target` name, which
    posts to that installation through the `DJANGO_SPIRE_METRIC_REMOTE_TARGETS` setting
    (a name-to-`{url, api_key}` mapping, falling back to `DJANGO_SPIRE_REMOTE_API_URL`
    and `DJANGO_SPIRE_REMOTE_API_KEY`). A remote registry can `record()` and `check()`
    against its target but not `build()`; run the build on the target installation.
  - The `metric_build` management command builds every registered registry. `--check`
    validates without writing and exits non-zero when anything is missing or drifted, for
    a CI gate, and `--registry` builds one registry by its dotted path.
  - The build also flags orphans: rows that exist in the database but are declared in no
    registry are listed as warnings (never deleted) and get `is_orphaned` set to `True`,
    while rows the registry declares get it cleared. The flag is idempotent — it mirrors
    the registry state at the last build — and `--check` never writes it. The domain,
    sub-domain, group, and statistic pages show a warning "Orphaned" badge (with a hover
    explanation) on list rows, detail cards, the statistics and storage tables, and the
    edit forms, and the admin lists the flag for domains and sub-domains.
  - Docs: `docs/app_guides/metric/registry.md`.
- `Seeder.unique(...)`, a field seed that guarantees the values it generates are unique
  both within the seeded batch and against rows already in the database. It takes exactly
  one base-value source: `field_seed=` (another field seed), `row_field=` (a row field
  name to copy from), or `row_value_callable=` (a callable that receives the row values
  generated so far). A collision gets a numeric suffix (`a`, `a-2`, `a-3`, ...) truncated
  to the field's `max_length`, and the seed disables the seed cache for its seeder.
  `UserSeeder`'s `username` is now seeded this way from the seeded email, so seeded users
  keep unique usernames within a batch, against existing users, and across re-seeds.

### Changes

- Migrated from `django-glue` v1.2.2 to v1.3.0. A confirmation's Cancel uses `$dispatch`,
  which arrived in 1.3.0.
- `FormComponent.form` and `ModelFormComponent.model` are declared with Glue's
  `Glue.child`, which replaces a `Glue.property` that returns a Glue object. A child
  declared this way is sent with each call its component makes, so a callable on a
  subclass can read `self.form` or `self.model` with what the user typed. Those calls are
  larger as a result; nothing else changes.
- A `ModelFormComponent` whose row no longer exists reports Glue's
  `model_instance_not_found` error, a 404, in place of a server error. A CRUD scroll's
  edit and delete actions report the same for a row outside its queryset.
- A failed Glue call tells the user. Spire's `base.html` registers `Glue.onError`, which
  shows one of three fixed messages as an error toast: the item no longer exists, the user
  lacks permission, or something went wrong. A component's own `onError`, or an
  application's `Glue.onError`, replaces it.
- A CRUD scroll removes a row from the list when editing or deleting it finds the row is
  gone.
- The `--primary` custom property is defined again, as Bootstrap's `--bs-primary`. Its
  definition was removed with the theme picker while the loader, the item hover, the
  panel borders, the button focus outline and the stepper went on using it, so those
  rules were dropped by the browser. A project gets it by compiling its theme again.
- The field seeding bot generates a row in a single forward pass split around the LLM
  fields by declaration order, instead of every non-LLM field before the LLM ones. A
  field declared after an LLM field can now consume the LLM-generated value (which
  `UserSeeder`'s `username` uses), and the fields declared before it still form the LLM
  prompt's context.
- The metric seeders' unique keys survive re-seeding: the `SubDomain`, `Statistic`, and
  `VisualRegion` seeders wrap their curated key lists in `Seeder.unique`, and the
  `Signage` seeder seeds its UUID key with `Seeder.fake.uuid4()`. Seeding onto an existing
  database, or seeding with `SEEDING_MULTIPLIER` above 1.0, now produces suffixed (or
  fresh) unique keys instead of a duplicate-key error.
- The Django admin's site header and title now read `Django <version> Spire
  <version> Admin Panel`, with `Glue <version>` included when django-glue is
  installed, applied from the core app config on startup.

### Fixes

- The page a password reset email links to renders again. Since 1.1.0 it raised
  `ValueError` for every link, because it still used the Glue field API from before 1.1.0.
  It is now a plain form like the other auth pages: it shows the form's errors, and a used
  or expired link asks the user to request a new one.
- `django_spire/form/delete_form.html`, included by `form/card/delete_form_card.html`,
  renders again. It raised the same `ValueError`; it now posts `should_delete` from a hidden
  input.
- The iOS install prompt on the auth pages shows Spire's icon by default. Its `app_icon`
  block pointed at `favicons/android-chrome-192x192.png`, which Spire does not ship; it now
  uses `favicons/android-icon-192x192.png`. A project that overrides `app_icon` is
  unaffected.
- The search, notification and account buttons in the open mobile menu take the side
  navigation's link color (`--side-navigation-link-color`). They used the primary color, so
  a theme whose side navigation background is its primary showed only the close button, and
  no way to log out. Themes whose link color is their primary, like the default, look the
  same. A project with its own compiled theme runs `spire_compile_scss` to pick this up.
- The account menu opened from the mobile menu keeps Bootstrap's dropdown colors. The side
  navigation's link colors reached its links, so a theme with white navigation links
  showed Change Password and Logout as white on the white dropdown. Side navigation link
  styles now leave links inside a `.dropdown-menu` alone.

### Chores

- Spire's Alpine components have JavaScript unit tests, run with `bun test` and in CI.

## v1.3.0

### Features

- The Celery task system was rebuilt as a worker/web split design (this module is in a working alpha state):
  - Worker tasks are authored with the `celery_task` decorator and run on a
    `CeleryTaskRunner` (a plain Celery `Task` subclass). `self.tracker` reports
    progress (`set_started`, `set_completed`, `update_state`, `update_count_progress`,
    cumulative progress, `set_retries`), and a `TaskDataModel` subclass registered
    as `meta_data_model` types `tracker.meta.data`. Mid-run updates are coalesced by
    a flusher thread that pushes them to the result backend at a fixed interval, so
    task code never blocks on backend I/O.
  - The worker writes only to the Celery result backend; the web process is the single
    writer of the `CeleryTask` row, syncing from the backend on every request through a
    state machine that drops stale and backwards transitions and keeps progress
    monotonic. Task outcomes are derived from the `CeleryTask` rows themselves.
  - `BaseCeleryTaskManager.send_task` validates kwargs, retries the send with
    exponential backoff, stamps `spire_*` headers, and records a FAILURE `CeleryTask`
    carrying a `CeleryExceptionResult` when the send itself fails (surfaced via
    `send_error_message` / `send_error_details`). Managers can opt into
    `dedupe_unready = True` to reuse an existing unready task instead of re-sending.
  - FAILURE tasks store a pickled `CeleryExceptionResult` (exception type, message,
    traceback) in the result column plus a formatted `exception_traceback` column,
    rendered in the task UI and the admin change page.
  - A new `celery:task:cancel` view (and an admin action) cancels a running task.
  - An embedded cron scheduler: subclass `CeleryScheduler` with `SchedulerTask` entries
    (an existing `BaseCeleryTaskManager` subclass + a 5-field cron string), register the
    class in `DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES`, and a daemon thread in the web
    process sends the task when its cron slot is due — no beat server. Slot claims are
    atomic per entry on a `CelerySchedulerTask` row, so multiple web instances agree, a
    down instance fires at most once on recovery, and missed slots are never replayed.
  - A background sweep thread resolves non-ready `CeleryTask` rows from the result
    backend in batches (up to `DJANGO_SPIRE_CELERY_SWEEP_TASK_LIMIT` per
    `DJANGO_SPIRE_CELERY_SWEEP_INTERVAL_SECONDS`), keeping task status fresh even when
    no page is viewing it. The `prune_stale_started_celery_tasks` management command
    resolves stuck STARTED tasks: it syncs tasks whose backend reached a terminal
    state, skips tasks still active on any worker, and marks the rest FAILURE. With
    `--include-pending`, stale PENDING tasks are synced when the backend already
    reached a terminal state and skipped (never stamped) otherwise, and the reaper
    pings the workers before stamping and skips the FAILURE stamp entirely when no
    live worker answers, so an unacked message that may still be requeued is not
    marked failed.
  - The scheduler and sweep threads start only in web processes:
    `is_web_server_process` requires a `runserver` / `runserver_plus` child or a
    WSGI/ASGI server binary (gunicorn, uwsgi, uvicorn, daphne, hypercorn), so Celery
    workers and scripts never run redundant background threads. The detection can be
    forced with the `DJANGO_SPIRE_CELERY_WEB_PROCESS` environment variable (true/1/yes
    or false/0/no).
  - A `check_celery_threads` management command reports OK/STALE/SKIPPED for the
    background sweep and cron scheduler threads from the freshness of each thread's
    claim row, with `--fail` exiting 1 on any STALE for cron/monitoring use.
  - New settings: `DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES`,
    `DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED`, `DJANGO_SPIRE_CELERY_SCHEDULER_TICK_SECONDS`,
    `DJANGO_SPIRE_CELERY_SWEEP_ENABLED`, `DJANGO_SPIRE_CELERY_SWEEP_INTERVAL_SECONDS`,
    and `DJANGO_SPIRE_CELERY_SWEEP_TASK_LIMIT`.
- A `scripts/git-hooks/pre-commit` hook lints staged Python files with ruff and
  blocks the commit on findings; install it with `just install-hooks`.

### Changes

- `Spire.ajax` honors a custom `CSRF_COOKIE_NAME`: it reads the cookie name from a
  `spire-csrf-cookie-name` meta tag (served by the `django_spire` context processor from
  `settings.CSRF_COOKIE_NAME`) instead of a hardcoded `csrftoken`.

### Fixes

- `Spire.ajax` no longer raises on a non-JSON response body (such as an HTML error
  page): a failed response resolves with `data: null`.
- Fixed typo in the rest api access list card to properly read `API Docs`.

## v1.2.3

### Fixes

- Moved as much inline CSS, JS and Alpine into separate files reducing base HTML size by 40% on average.

## v1.2.2

### Breaking

- Migrated from `django-glue` v1.2.1 to v1.2.2. A Glue component in a directory inside a
  `components` package now has that directory in its tag: a class in
  `app/components/cards/fancy.py` is `app/cards/fancy`, where it was `app/fancy`, and the
  old tag raises `GlueComponentRegistrationError`. Add the directory to the tag, or import
  the class in `components/__init__.py` to keep the short one. A component in a module
  directly inside `components/` is unaffected, and Spire's own components need no change.
  The [django-glue changelog](https://django-glue.stratusadv.com) has the full list.

### Added

- `tabular-nums`, a utility class that sets `font-variant-numeric: tabular-nums` so the
  digits in a column of amounts line up.
- A stepper, for a numbered sequence of steps with done, current and upcoming states. It
  is a set of classes with no template: `stepper` on the list, `stepper-step` on each
  step with `is-done` or `is-current`, and `stepper-mark` on the circle. `stepper-vertical`
  stacks the steps and `stepper-connected` draws a line between them. See
  [Stepper](../components/stepper.md).

## v1.2.1 - October 8, 2026

### Changed

- Migrated from `django-glue` v1.2.0 to v1.2.1. It fixes a formset refusing a new
  `ModelForm` row, with "Submitted form token does not belong to this formset row", after
  that row had made a call of its own, such as loading a field's choices or validating.

## v1.2.0 - October 6, 2026

### Breaking

- Migrated from `django-glue` v1.1.0 to v1.2.0. The changes a project is most likely to
  meet (the [django-glue changelog](https://django-glue.stratusadv.com) has the full list):
  - `DJANGO_GLUE_COMPONENTS_ROOT` is removed. Replace it with
    `DJANGO_GLUE_COMPONENTS = {'DIRS': [<root>], 'APP_DIRS': True}`, which is shaped like
    Django's `TEMPLATES`. A project that still sets the old name fails the system check
    `django_glue.E004`.
  - The component modules moved into the `django_glue.glue.components` package.
    `django_glue.glue.component` and `django_glue.glue.component_registry` no longer
    exist; import `Component` and `component_registry` from `django_glue.glue.components`,
    or subclass `Glue.Component`.
  - A component's re-render keeps the child components already on the page instead of
    re-stamping them. A child that must redraw with its parent declares `rerender_on` or
    is stamped with `rerender_with_parent`.
  - A formset's `save()` saves nothing when any row is invalid; it previously saved the
    valid rows.
  - A component is set up in `__post_init__(self, request)`. `get_view_kwargs()` and
    `get_context_data()` are removed, and a class that still defines one raises
    `TypeError` when it is defined. `mount()` is deprecated; rename it to `__post_init__`.
    A component's template reads its values from `component`, and page context such as
    navigation goes in `self.context_data`.
  - `layout_template` is renamed `view_template`, as a class attribute and as an
    `as_view()` argument.
- `FormComponent` no longer defines `get_context_data()`, so its template context no longer
  has `glue_form`. A template rendered by a `FormComponent` reads the form's path as
  `{{ component.glue_form_path }}`. `django_spire/glue/form/modal_form.html` falls back to
  it, so a template that extends it needs no change. A subclass that overrode
  `get_context_data()` moves that code to `__post_init__` or onto the component.
- Removed the `django_spire.contrib.session` package, as it was no longer used. Session
  management is handled by `django-glue` going forward. This removes:
  - `django_spire.contrib.session.controller.SessionController`.
  - The `session_controller_to_json` template tag
    (`django_spire.contrib.session.templatetags.session_tags`).
  - The client `Spire.session.Controller` class. `django_spire/js/session.js` is deleted
    and no longer loaded by `django_spire/base/base.html`.
- `django_spire.testing.playwright.components.base_session_filter_form` is renamed to
  `django_spire.testing.playwright.components.filter_form`. `FilterForm` is still exported
  from `django_spire.testing.playwright.components`, so only imports of the module path
  need updating.
- `DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY` and
  `DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY` are renamed to
  `DJANGO_SPIRE_METRIC_STATISTIC_KEY` and `DJANGO_SPIRE_METRIC_SUB_DOMAIN_KEY`, the
  statistic and sub-domain that metric click tracking records against. A project that
  still sets the old names silently loses its tracking target; rename them in settings.

### Features

- New `RemoteClickMiddleware`
  (`django_spire.metric.domain.statistic.middleware.remote`) for sites that track clicks
  without running the metric database themselves: each tracked click (same rules as the
  local `LocalClickMiddleware`: GET, 200, `text/html`, skipping `/admin/`, `/api/`,
  and XHR) is POSTed to
  `{DJANGO_SPIRE_REMOTE_API_URL}/api/v1/metric/domain/statistic/{statistic_key}/record`
  with an `X-API-Key` header. It dispatches on a background thread by default, imports
  no `django_spire` modules (stdlib + `requests` + `django.conf` only), and is a no-op
  unless `DJANGO_SPIRE_REMOTE_API_URL`, `DJANGO_SPIRE_REMOTE_API_KEY`,
  `DJANGO_SPIRE_METRIC_STATISTIC_KEY`, and `DJANGO_SPIRE_METRIC_SUB_DOMAIN_KEY` are all
  set.
- The metric visual "Generate Stoplight" action is removed, with its
  `set_default_conditions` URL and `visual.services.factory.create_default_conditions()`.

### Changes

- A metric visual's detail card links to its statistic group and its statistic separately.
- Monthly chart labels always show the year, as `Jan 26`.
- `FormComponent` subclasses `Glue.Component` instead of importing `Component` from a
  `django-glue` internal module.
- `spire_startapp` no longer scaffolds session-backed list filtering. A generated app has:
  - no `constants.py` (it only held `LIST_FILTERING_SESSION_KEY`), no
    `<Model>ListFilterForm`, and no list filter form template;
  - a queryset that subclasses `HistoryQuerySet` alone, without `SearchQuerySetMixin`,
    `SessionFilterQuerySetMixin`, or a `bulk_filter` method;
  - list page and list items views that load `objects.active()` instead of calling
    `process_session_filter`, and no `filter_session` in the page context.
- The knowledge entry form view no longer glues an unused `entry` model.

### Fixes

- The comment modal no longer crashes on open. Its `Glue.model` call now exposes the
  `information` field at `CHANGE` access, so the comment text is editable.
- Metric charts and indicators fill their cards on signage displays and presentation
  slides. Their heights are set by `--spire-chart-height` (default `350px`) and
  `--spire-indicator-min-height` (default `240px`).
- A new visual condition, visual reference or signage presentation is added at the next
  free order position.
- A visual ignores its deleted conditions when it works out its current condition and
  gauge maximum.
- A visual with no conditions no longer shows a "No data" status badge.

### Chores

- Removed the "QuerySet Utilities" guide (`docs/app_guides/contrib/queryset.md`) from the
  docs. It described `django_spire.contrib.queryset`, which no longer exists.
- `.backplan/` is ignored by git.

## v1.1.0 - September 27, 2026

### Breaking

- Migrated from `django-glue` v1.0.1 to v1.1.0. The most visible changes:
  - `django_glue.middleware.GlueViewMiddleware` is now required as the **last** entry in
    `MIDDLEWARE` (a system check errors if it is missing or misordered).
  - Sub-services are exposed with `Glue.namespace(...)` instead of `Glue.attr(...)`;
    `@Glue.attr` now marks individual service methods the client may call.
  - `GlueResponse` takes the redirect directly (`GlueResponse(redirect={'url': ...})`)
    instead of nesting it under `result`.
  - The Alpine core is no longer loaded from the CDN: `django-glue` bundles it (with its
    morph plugin) and owns Alpine startup. The `@alpinejs/*` plugin scripts stay in
    `base.html` and register against the runtime Glue exposes.

### Features

- New `FormComponent` / `ModelFormComponent` (in `django_spire.core.glue.components`) for
  exposing a single form as a Glue component, with `Spire.modal.dispatchGlueComponent()`
  and `Spire.modal.dispatchGlueHtml()` client helpers that show Glue-rendered content in
  the dispatch modal and resolve when it closes.
- Choice fields can render HTML labels: pass `label_formatter` to `Glue.choices(...)` to
  pre-render each choice label (see the showcase `formatted_category` widget).
- Glue scroll lists (notification dropdown/list, task list, and the shared
  `glue/scroll/scroll.html`) now load pages through the queryset's own continuation with
  generation-ordered loads, so an overtaken reset or a page load in flight can no longer
  overwrite newer results. Querysets bound for scrolling accept `batch_size`.
- Metric visuals: charts now display a unit-based window (`display_unit_count` on the
  visual, defaulting to 8 days / 12 weeks / 13 months) with period labels ("Today",
  "Week to date", "Month to date"), a `value_date` browse parameter on the detail page
  for historical dates, and a distinct "no matching data" state instead of a false zero.
  Gauge, pie, and line/bar rendering were reworked (unit x-axis labels, overlapping
  labels hidden, nicer axis ceilings). The signage display page was updated to match.
- Celery admin: a state filter (standard plus observed states), human-readable state
  display, and a readable result column on the `CeleryTask` change form.

### Changes

- The `Visual.date` field was removed; visuals are always computed as of today, and the
  detail page's `value_date` parameter browses history (migrations `0007_remove_visual_date`,
  `0008_visual_display_unit_count`).
- Celery race-condition fixes: the tracker pushes state/meta to the Celery backend instead
  of writing the `CeleryTask` row directly, and `CeleryTaskService` merges the completed
  meta into the row when it polls a ready result (meta `data` is merged, not replaced).
- The help desk ticket list now exposes explicit Glue fields instead of `__all__`.
- Test project Celery app now runs with `task_acks_late`, `task_reject_on_worker_lost`,
  soft/hard time limits, and broker retry on startup.

### Fixes

- `CeleryTaskTracker.update_cumulative_progress` now raises `ValueError` (instead of
  `TypeError`) when no cumulative target was set, and clamps progress at the target.
- The Celery admin change form no longer crashes on task rows with an empty or corrupt
  result blob.

### Chores

- `playwright-limelight` (dev) is pinned from PyPI instead of a git revision.

## v1.0.4 - September 21, 2026

### Fixes

- Fixed the `Signage` displays to be more compatible with a wider variety of physical displays.

### Changes

- `Statistic` now includes the `StatisticGroup` when being referenced or generating a key for accessing via internal 
  and external API's.

## v1.0.3 - September 16, 2026

### Changes

- The search palette (Ctrl/Cmd-K) now covers the metric and API apps: domains, sub-domains, statistic groups, statistics, visuals, presentations, signages, and API access keys, each with permission-gated create commands.
- API access keys now have a detail page (user access, base permission, key hint, and created date) and the API access list page includes a recent activity log.
- Seeding now scales requested seed counts by the `SEEDING_MULTIPLIER` environment variable (default `1.0`, configured in `django_spire.contrib.seeding.seeding_settings`), with an `ignore_multiplier` flag on `Seeder` to opt a seeder out and always seed at the exact requested count.

### Fixes

- Fixed API keys with `has_super_access` being rejected by the base and user permission checks in `ApiKeySecurity.authenticate`.
- Widened the Celery task `state` field to 32 characters (previously 16) so longer states such as `RECEIVED` save correctly, with over-long states truncated with an ellipsis and states rendered as human-readable labels on the task page.
- Fixed the navigation-link click prefetch not sending the `X-Requested-With` header, which broke the click-tracking feature.
- Fixed submit button labels becoming unreadable on the primary color in dark mode (buttons now force white text).
- Deleting a domain, statistic group, or statistic now detaches its visuals (their statistic reference is cleared) instead of leaving them pointing at deleted statistics; deleting a visual now soft-deletes its conditions and references and detaches its regions and slide sections.
- Fixed visual and slide-section forms listing soft-deleted statistics/visuals as selectable options.
- Fixed the signage form allowing a slide display duration of zero seconds.

## v1.0.2 - September 9, 2026

### Fixes

- Fixed broken permission guarding for navigation links to knowledge base
- Fixed missing permission group allocation for knowledge base collections
- Fixed collections unable to be assigned no parent upon edit
- Fixed issue causing `Seeder.fake.date_between` to attemtp to make the date timezone aware 

## v1.0.1 - September 3, 2026

### Fixes

- Updated API security logic to match forms & display.
- Fixed Auth User page from displaying 2 dispatch modals.
- A required `select_widget.html` field with no placeholder no longer looks filled in while actually submitting empty.
- Glue scroll lists (`glue/scroll/scroll.html`) now bust their cached query results on reset, so a row removed or filtered out elsewhere (e.g. by a delete, or an edit that changes which list it belongs in) no longer reappears from stale cached data.

## v1.0.0 - September 2, 2026

### Overview

First stable release of the v1 line. Everything the 0.x series shipped is here (last
release: v0.32.11), rebuilt on Django 6, `django-glue` v1.0.0, and Python 3.12. v1 adds
four new framework apps (API, Celery, file, metric), a rewritten seeding system, a
service layer, an event-based activity/audit trail, a global search palette, and an
overhauled admin, navigation, and front-end stack.

### Breaking

- Migrated from `django-glue` v0.8.x to `django-glue` v1.0.0. Every glue-enabled
  template, view, and client call uses the new attribute/widget syntax; `js_url` was
  renamed to `glue_url` and moved onto the `Glue` client global.
- Minimum Python raised to 3.12; test project restructured from a flat layout to an
  app-based layout (`test_project/app/`).
- `ApiAccessLevelChoices` replaced by `ApiPermissionChoices` (level → permission), with
  granular view/add/change/delete API permissions.
- `django_spire.sync` removed (synchronization functionality dropped) and
  `django_spire.contrib.sync` with it.
- `django_spire.changelog` app removed, replaced by the `render_markdown` template tag.
- Profiling middleware removed; `django_spire.theme` app removed (theming now lives in
  `core` SCSS variables + `theme.js`).
- Seeding rewritten: `cache_enabled` removed, seeder API and configuration changed, old
  seeders must be migrated to the new field-seeder types.
- Per-app view-level auth controllers (`django_spire.auth.controller`,
  `help_desk/auth/controller.py`, etc.) removed. Use the `permission_required` decorator
  (`django_spire.auth.permissions`) instead.
- `spire_opencode` management command and bundled agent/skill files no longer ship in the
  package.
- Legacy `django_spire.core` modules relocated to the package root (`constants.py`,
  `conf.py`, `exceptions.py`, `settings.py`, `shortcuts.py`, `tools.py`, `urls.py`);
  `contrib.breadcrumb` replaced by `contrib.navigation`.
- App URL patterns are auto-discovered through `URLPATTERNS_INCLUDE` +
  `URLPATTERNS_NAMESPACE`; apps now split URL config into `urls/page_urls.py` and
  `urls/form_urls.py`.
- `distinct` query handling removed from scroll/querysets.
- Contrib helpers consolidated: `pagination`, `progress`, `performance`, `gamification`,
  `html_renderer`, `generic_views`, `help`, `choices`, and `service` were removed or
  merged into `responses`, `form`, `ordering`, and `constructor`.
- New installs must add `django_spire.history.activity.middleware.ActivityUserMiddleware`
  to `MIDDLEWARE` after `AuthenticationMiddleware` (system checks `W001`–`W003` flag it).
- `Site` object now reads `DJANGO_SITE_NAME`/`DJANGO_SITE_DOMAIN` instead of a fixed host.
- `Domain.set_delete()` overridden so deleting a domain cascades through sub-domains,
  statistic groups, and statistics.

### Features

- **`django_spire.api`** — REST API backend (django-ninja, mounted at `api/v1/`) with
  hashed API-key authentication, granular permission levels, and an access management UI.
- **`django_spire.celery`** — Celery task queue support: task manager, progress tracking,
  results, toast/detail UI, and infinite-loop detection and prevention.
- **`django_spire.file`** — generic file management: uploader/handler, extensions,
  temporary media, AJAX upload endpoints, admin, and seeding.
- **`django_spire.metric`** — metrics system:
  - `domain` — domain/sub-domain CRUD, admin panels, infinite scrolling, auto-slugged
    sub-domain keys, and seeding.
  - `statistic` — statistics grouped under a domain with daily/weekly/monthly intervals
    and number/percentage/currency values; `StatisticValue` rows per reference, indexed
    for interval/reference lookups; page-view and click tracking via
    `StatisticClickMiddleware` written by a background queue; a REST API
    (`metric/domain/statistic`) to record and read values; aggregations, retention
    pruning (`prune_metric_statistic_values`), and tracking caps.
  - `visual` — indicator, line, bar, area, pie, and gauge ECharts; threshold conditions
    with state colors and tolerance; references for dataset series; named, optionally
    live-updating visual regions rendered anywhere via `render_visual_region`.
  - `presentation` — slide-based presentations with grid-positioned sections.
  - `signage` — signage displays with ordered presentation links and a public display view.
  - `report` — report registry and rendering with sub-navigation and a print view.
- **`django_spire.contrib.rest`** — queryset-like access layer for external REST sources:
  schema/schema-set architecture, bearer auth, pagination, and prefetch support.
- **`django_spire.contrib.converters`** — convert Django models to Pydantic classes,
  data dicts, and enums.
- **`django_spire.contrib.navigation`** — navigation/breadcrumb model extracted from the
  old breadcrumb module.
- **`django_spire.contrib.chart`** — ECharts helpers for visual components.
- **Activity & audit trail** (`django_spire.history.activity`) — event-based activity
  records: automatic `created`/`updated`/`deleted` on save and soft-delete, bulk
  activities for `bulk_create`/`bulk_update`/`update`/`delete`, m2m `added`/`removed`
  activities, request-user attribution via `ActivityUserMiddleware`, and
  `activity_user()` for off-request work (Celery tasks, management commands).
- **Search palette** (`django_spire.core.search`) — Ctrl/Cmd-K global search across
  registered models and commands via a `Search` subclass registry
  (`DJANGO_SPIRE_SEARCH_REGISTRY`), with per-model searchable fields, commands, and
  permissions.
- **Seeding system overhaul** — new field seeder types (callable, custom, exclude, file,
  index, mutate, model with ordered/random foreign keys, LLM, static), seeding meta,
  init/mutate seed logic, multi-FK support, and optional faker/LLM data.
- **Infinite scrolling** — `GlueScroll` for task, domain, sub-domain, statistic, and
  notification lists with customizable scroll increments and ordering/filtering overrides.
- **Task app** — infinite nested tasks, rich task cards, task duplication, interactive
  status updates, and child lists.
- **Auth** — password change enforcement on first login, email lowercase normalization,
  user and group management pages with permission matrices, MFA page, SMS verification
  (`auth/sms`) with `DJANGO_SPIRE_AUTH_SMS_*` settings, and full password reset flows.
- **Glue widgets** — required-field red asterisks, `field-input`/`field-change`/
  `field-focus`/`field-blur` events, search-and-select and multi-search widgets, decimal
  precision, and multi-file upload support.
- **Markdown rendering** — `render_markdown` template tag with code blocks, fenced-code
  rendering, and Editor.js support, replacing the changelog app.
- **Front-end** — button loading states, slide button component, brand logo, `.woff2`
  fonts, consolidated SCSS with theme CSS variables, tightened navigation with responsive
  icons and FOUC prevention, and `preconnect`/`defer` for first-load performance.
- **Knowledge** — entity admin panels, collection navigation and reordering, entry import,
  version editor and publish flow, code blocks, SMS integration with webhook handling and
  `KnowledgeSearchRouter` intent routing, and a search-index rebuild command.
- **Help desk** — full CRUD refactor with action buttons, sorting, breadcrumbs, and a
  services layer.
- **Comment / notification / file / REST client** — CRUD pages, breadcrumbs, app
  notification list/dropdown, and AJAX endpoints.
- **Admin** — `SpireModelAdmin` (`model_class` self-configuration, auto `list_display`
  and `search_fields` that exclude secret fields, `list_select_related` population),
  admin link helpers (`admin_change_link`, `external_link`, ...), query-count guarded
  admin tests, and a Playwright walkthrough of every changelist and change form.
- **Tooling** — `spire_startapp` (interactive app generator), `spire_flush`,
  `spire_remove_migration`, `spire_compile_scss`, `prune_metric_statistic_values`, and
  `rebuild_knowledge_search_index` management commands; per-app test suites, a REST test
  app, and Playwright E2E CI.
- **New settings** — `DJANGO_SPIRE_SEARCH_REGISTRY`, `DJANGO_SPIRE_AUTH_SMS_*`,
  `DJANGO_SPIRE_DEFAULT_THEME_MODE`, `DJANGO_SPIRE_METRIC_VISUAL_REGIONS`,
  `DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX`, `DJANGO_SPIRE_METRIC_RETENTION_DAYS`,
  `DJANGO_SPIRE_METRIC_TRACKING_QUEUE_MAXSIZE`, and
  `DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY`/`SUB_DOMAIN_KEY`.

### Changes

- Dependencies: `django-glue` v0.8.x → v1.0.0, `django` bumped to ≥ 6.0.6, Dandy updated
  for AI model configuration, `robit` pinned to v0.4.9.
- All buttons converted to styled template components; error pages and field/scroll
  templates rewritten.
- View and pagination code refactored to the glue v1 attribute patterns.
- Fonts switched from `.ttf` to `.woff2`; SCSS/CSS packaging consolidated and hardcoded
  colors moved to CSS variables.
- Breadcrumbs standardized across every app via the navigation module.
- Session controller hardened against redefinition and `KeyError` purges.
- Auth group permission data now loads through Glue computed attributes instead of a
  separate template-context payload.
- `multi_file_field.html`, AI chat, and knowledge views updated for `django-glue` v1.0.0.
- Infinite-scroll ordering and filtering can be left empty/overridden on the glue base
  scroll.
- Knowledge, help-desk, comment, notification, file, and REST client broken links and
  breadcrumbs fixed.

### Security

- `AuthUser` admin no longer renders `password` as a plain-text input (editing a user
  previously stored the typed value unhashed).
- MFA codes no longer appear in the `MfaCode` admin list or search, and `MfaCode` is
  read-only; codes can be deleted but not created/edited.
- `ApiAccess` can no longer be created through the admin; keys are generated and hashed
  through the API access form. `ApiAccess.permission` is editable again.
- Notification URLs pointing at `javascript:`/`data:` render as text, and external links
  carry `rel="noopener noreferrer"`.

### Fixes

- Admin `format_html` calls pass url/label as arguments (fixes `TypeError` on Django 6.0).
- Generic foreign key columns in comment, file, history, activity, and viewed admins no
  longer 500 when the related model is not registered in the admin; related objects are
  prefetched to avoid one query per row.
- `ChatMessage.intel` and `Domain`/`SubDomain` admin search no longer raise `FieldError`/
  `ValidationError`; per-row `count()` queries replaced with queryset annotations.
- Bulk tagging in knowledge admins is capped at 25 rows to avoid request timeouts;
  all-read-only admins no longer offer a blank add form.
- Decimal Glue fields accept arbitrary precision; slate select widgets no longer freeze
  the browser on foreign-key choice fields; search-and-select dropdown positioning fixed
  inside modals.
- Help-desk and metric domain/sub-domain services are no longer exposed as deletable Glue
  attributes.
- App notifications and dropdowns restored; `safe_redirect_url` adopted across domain,
  statistic, REST, and task redirects.
- Celery infinite-loop detection hardened; `SessionController` guard and purge fixed.
- Tag rendering bug in the task app, missing login-required decorators on several views,
  and mobile navigation links fixed.
- Seeder OOM issues, LLM error handling, and foreign-key seeding bugs fixed.

### Removals

- `django_spire.sync` and synchronization functionality.
- `django_spire.changelog` app.
- Profiling middleware and `django_spire.theme` app.
- Per-app auth controllers and the `spire_opencode` command.
- `ApiAccessLevelChoices` (replaced by `ApiPermissionChoices`).
- `cache_enabled` from the seeder configuration.
- `distinct` query functionality and tests.
- Hardcoded color values (migrated to CSS variables).

### Upgrade notes

1. Read the breaking-change list above before upgrading; the glue v1 migration and the
   seeding rewrite require the most rework in existing apps.
2. Add `ActivityUserMiddleware` to `MIDDLEWARE` and confirm the system checks are clean.
3. Regenerate or migrate existing seeders to the new field-seeder API.
4. Replace any `javascript:`/`data:` notification URLs and re-issue API keys (old keys
   were hashed under the previous scheme).
