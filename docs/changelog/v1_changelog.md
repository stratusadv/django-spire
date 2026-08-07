## v1.0.1-rc2 - August 6, 2026

#### Fixes

- Fixed Glue form select widgets causing browser freezes with foreign key choice fields.
- Improved search-and-select dropdown positioning and stacking inside modals.

## 1.0.1-rc1 - August 6, 2026

#### Changes

- Auth group list permission data now loads through Glue queryset computed attributes instead of a separately serialized template context payload
- Domain and subdomain services are no longer exposed as Glue attributes, which was causing a bug
- Updated `multi_file_field.html` to work with `django-glue` v1.0.0.

#### Fixes

- Refactored AI Chat and Knowledge system to work with v1.0.0 and `django-glue` v1.0.0.

## 1.0.0 - July 31, 2026

#### Breaking

- Migrated from `django-glue` v0.8.x to `django-glue` v1.0.0a1 — all templates, views, and glue references updated to new syntax and patterns
- Removed `django_spire.sync` module — synchronization functionality removed
- Removed `django_spire.changelog` app — replaced with `render_markdown` template tag
- Removed profiling middleware module
- Removed `cache_enabled` parameter from seeding system
- Minimum Python version raised to 3.12
- Removed `ApiAccessLevelChoices` — replaced with `ApiPermissionChoices` (level → permission)
- Test project refactored from flat structure to app-based layout
- `set_delete()` method overridden in domain classes
- Removed `distinct` tests (distinct was removed from query handling)

#### Features

- **New App `django_spire.api`** — REST API backend with API key authentication, granular permission levels (view/add/change/delete), and access management UI
- **New App `django_spire.celery`** — Celery task queue support with task tracking, progress monitoring, infinite-loop prevention, and contextual monitoring
- **New App `django_spire.metric.domain`** — Domain/subdomain management with CRUD, admin panels, infinite scrolling, and seeding
- **New App `django_spire.metric.visual`** — Visual metric components (initial structure)
- **New App `django_spire.file`** — Generic file management with uploader/handler module, file seeding, and breadcrumb navigation
- **New Module `django_spire.contrib.rest`** — Django queryset-like pattern for connecting to external REST data sources with Schema/SchemaSet architecture, bearer auth, and prefetch support
- **New Module `django_spire.contrib.converters`** — Utilities to convert Django models to Pydantic classes, data dictionaries, and enums
- **New Module `django_spire.contrib.navigation`** — Navigation utilities extracted from breadcrumb module
- **Seeding System Overhaul** — Complete refactor with new field seeder types (callable, file, index, model, mutate), seed factory pattern, seeding meta system, init/mutate seed logic, and LLM seeding support via `SEEDING_USE_LLM` setting
- **Infinite Scrolling** — Added to domain, subdomain, task pages, and scrollable containers with customizable scroll increments
- **Generic Confirmation Modal Views** — `dispatch_confirmation_modal_form_content` for standardized confirmations (e.g., mark-as-completed)
- **Task Duplication & Interactive Status Updates** — Task app with rich task cards, nested tasks, and interactive status toggling
- **Auth System** — Enforce password change on first login, email lowercase normalization, updated user forms
- **Opencode Integration** — New agents, skills, and management commands for AI-assisted development
- **Button Loading States** — `base_button.html` updated with loading state for `x_button_click` and `button_modal_href`
- **Slide Button Component** — New slide button template
- **Markdown Renderer** — Custom markdown rendering template tag replacing changelog app
- **Django Spire Logo** — Brand logo added
- **Navigation Improvements** — Nav tightening, responsive icons, FOUC prevention, targetable navigation classes
- **View-Level Auth Controllers** — All apps updated with `AppAuthController` permission checks

#### Changes

- Updated `django-glue` requirement from `v0.8.13` → `v0.8.14` → `v1.0.0a1`
- Updated `Dandy` requirement for AI model configuration
- Updated `Robit` to `v0.4.9`
- Switched font files from `.ttf` to `.woff2` for performance
- Replaced all `django_glue` template references with `django_glue_old` during v1 migration, then fully migrated to glue v1 attribute syntax
- Refactored all views and pagination to support glue v1 patterns
- Converted all buttons to styled template components
- SCSS/CSS packaging cleanup — consolidated SCSS compilation, removed hardcoded colors, improved theme variables
- Help desk app — full CRUD refactoring with action buttons, sorting, and breadcrumbs
- Knowledge base — breadcrumb fixes, entity admin panels, delete view fixes, collection navigation improvements
- Comment app — breadcrumb and link fixes
- Notification app — link and breadcrumb fixes
- Breadcrumb system — cleaned up and standardized across all apps
- Domain/subdomain — admin panels, CRUD implementation, glue v1 integration, UI polishing
- Session controller — guard against redefinition, purge fix for `KeyError`
- `Site` object — pull from `DJANGO_SITE_NAME`/`DJANGO_SITE_DOMAIN` env variables
- Added `preconnect` and `defer` for first-page-load performance
- Testing framework — expanded with app-specific test suites, test factories, and REST test app
- CI pipeline — added v1/base branch triggers

#### Fixes

- Celery infinite loop detection and prevention
- Error page templates (`error_page.html`, `scroll.html`)
- Field template (`field.html`) rendering
- Form error rendering and redirect behavior
- Tag bug in task app
- Broken links across help desk, file, comment, notification, knowledge, and domain apps
- Scroll behavior fixes in containers and tasks
- Missing login-required decorators on multiple views
- Auth template/URL issues
- API access form fixes
- Seeding — OOM issues, LLM error handling, FK seeding bugs, multiple FK method support
- Navigation link not working in mobile
- Admin panel many-to-many relationship exclusions
- Report sub-navigation display
- `add_form_activity` verb logic
- Theme CSS and responsive icon fixes
- `toggleLoadingOverlay`/`toggleLoadingSpinner` separation and behavior

#### Removals

- `django_spire.sync` module (functionality removed)
- `django_spire.changelog` app
- Profiling middleware
- `ApiAccessLevelChoices` (replaced by `ApiPermissionChoices`)
- `cache_enabled` from seeder configuration
- `distinct` query functionality and tests
- Hardcoded color values (migrated to CSS variables)

#### Unfinished

- `django_spire.metric.domain` — domain management is functional, visual/metric layer pending
- `django_spire.metric.visual` — initial structure only, not yet feature-complete
