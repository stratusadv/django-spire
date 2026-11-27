# EmailNotification multi-recipient `to` field & validation

- Developer: Chase Mossing (chasem@stratusadv.com)
- Status: Executed
- Date: 2026-11-27-11-08

## End State

`EmailNotification` replaces `to_email_address` with a validated `to = models.JSONField(default=list)` field matching `cc` and `bcc`, rejects non-list inputs, invalid email addresses, empty `to`, and case-insensitive duplicate recipients within or across `to`/`cc`/`bcc` on `full_clean()`, `save()`, `bulk_create()`, and `bulk_update()`, formats `SendGridEmailHelper.template_data['to']` as `', '.join(self.to)`, safely migrates existing `v0`/`v1` database rows via chunked reversible migration `0004` before dropping `to_email_address`, and passes notification, help desk, admin smoke, migration, and `ruff` checks.

## Observable Concern

Almost every `EmailNotification` in Spire and downstream apps is created via `.objects.create()` or `.objects.bulk_create()` rather than a `ModelForm`, so Django field `validators` alone will silently let invalid or duplicate recipients into the database; validation must run in `clean()`, `save()`, `bulk_create()`, and `bulk_update()`, while also keeping `blank=True` on optional `JSONField`s (`cc`, `bcc`, `context_data`), safely backfilling dirty legacy `v0` rows (`to_email_address`, `cc`, `bcc`) before dropping `to_email_address`, and updating `django_spire/contrib/admin/tests/factories.py` (which seeds `{}` for every `JSONField`) so `AdminSeedCoverageTests` keeps passing.

## Current State

Verified 2026-11-27 against the working tree (`django-spire` v1.7.0, Django 6.0.9, `django-sendgrid-v5` 1.3.1):

- `django_spire/notification/email/models.py`:
  - `to_email_address = models.EmailField()` (single `varchar(254)`, `blank=False`).
  - `context_data = models.JSONField(default=dict)`, `cc = models.JSONField(default=list)`, `bcc = models.JSONField(default=list)` — no validators, no `blank=True` (Django treats `[]` and `{}` as empty during `full_clean()` when `blank=False`).
  - `__str__` returns `f'{self.notification.title} - {self.to_email_address}'`.
- `django_spire/notification/email/migrations/`: latest migration is `0003_emailnotification_attachments.py` (identical between `v0.32.13` and `v1.7.0`).
  - Earlier commit `496f041f` briefly defined `cc`/`bcc` with `default=dict`, and `EmailHelper` accepted bare `str` for `cc`/`bcc`, so production DBs in older `v0` apps may hold `{}` or bare strings in `cc`/`bcc`.
  - Existing single-step schema + data migration precedent: `django_spire/file/migrations/0002_alter_file_related_field_alter_file_size.py` (1,000-row `iterator()` + `bulk_update()` chunks, `AddField` → `RunPython` → `RemoveField`).
- `django_spire/notification/email/helper.py`:
  - `EmailHelper.__init__` reads `email.to_email_address`, `email.cc`, `email.bcc` with `isinstance(..., str)` list wrapping.
  - `SendGridEmailHelper.__init__` sets `self.template_data['to'] = notification.email.to_email_address`.
  - `sendgrid_backend/mail.py` natively iterates `msg.to`, `msg.cc`, `msg.bcc` into one SendGrid `Personalization`, raises `ValueError` if `to` is empty, and SendGrid v3 returns HTTP 400 on case-insensitive duplicate emails within or across `to`/`cc`/`bcc`.
- `django_spire/notification/email/querysets.py`: `EmailNotificationQuerySet` inherits `HistoryQuerySet` and `NotificationContentObjectQuerySet`; has no recipient lookup helper and no bulk validation hooks.
- `django_spire/notification/email/admin.py`: `list_display = ('id', 'notification', 'to_email_address')`, `search_fields = ('id', 'to_email_address')`. Django 6.0 registers `JSONIContains` on `JSONField`.
- `django_spire/contrib/admin/tests/factories.py:52`: maps all `models.JSONField` to `{}` when seeding models for `AdminSmokeTests` and `AdminSeedCoverageTests`.
- Internal & `test_project` callers:
  - `django_spire/help_desk/services/notification_service.py:104-139`: builds `EmailNotification(notification=..., to_email_address=...)` and saves via `EmailNotification.objects.bulk_create(...)`.
  - `test_project/app/notification/forms.py:28-30`: creates `EmailNotification(notification=self.instance, to_email_address=self.data.get('email'))`.
  - `test_project/templates/notification/item/list_item.html:17` and `test_project/templates/notification/modal/process_modal.html:32`: render `{{ notification.email.to_email_address }}`.
  - `django_spire/notification/email/tests/`: has `factories.py`, `test_apps.py`, `test_models.py`, `test_processor.py`, `test_querysets.py` (no `test_validators.py`, `test_helper.py`, or migration tests yet).
- Docs: `docs/app_guides/notification/email_notifications.md` and `docs/changelog/changelog.md`.
- Lint/format: `.venv/bin/ruff` using `ruff.toml` (single quotes, line-length 120, `select = ["ALL"]` with repo ignores). Test runner: `just test-app <path>` against Postgres test DB on localhost:5439.

## Plan

1. Add reusable `EmailListValidator` in `django_spire/notification/email/validators.py`
   - Implement a `@deconstructible` `EmailListValidator(allow_empty: bool = True)` (serves email validation for `to`, `cc`, `bcc` across forms, admin, models, and migrations).
   - Reject non-`list` values (`str`, `dict`, `int`, `None`, etc.), non-`str` entries, empty strings, entries with leading/trailing whitespace, invalid emails via `django.core.validators.validate_email`, and case-insensitive duplicates within the list.
   - Reject empty list when `allow_empty=False`.
   - Done when `django_spire/notification/email/tests/test_validators.py` passes covering valid lists, empty list toggle, invalid types, malformed emails, whitespace, case-insensitive duplicates, and `deconstruct()`.

2. Update `EmailNotification` model in `django_spire/notification/email/models.py`
   - Replace `to_email_address` with `to = models.JSONField(default=list, validators=[EmailListValidator(allow_empty=False)])` (serves multi-recipient delivery matching `cc`/`bcc`).
   - ~~Keep `to_email_address = models.EmailField(blank=True, default='')` with `DeprecationWarning` fallback.~~ (Superseded by Deviation 1.)
   - Add `blank=True` and `validators=[EmailListValidator()]` to `cc` and `bcc`; add `blank=True` to `context_data`.
   - Add `validate_recipients()` called by `clean()`, `save()` (when `update_fields` is `None` or includes any of `to`, `cc`, `bcc`), and queryset bulk writes:
     - Validate `to` (`allow_empty=False`), `cc` (`allow_empty=True`), and `bcc` (`allow_empty=True`) via `EmailListValidator`.
     - Reject case-insensitive duplicate emails across `to`, `cc`, and `bcc`, attaching the `ValidationError` to the conflicting field (`cc` or `bcc`).
   - Update `__str__` to render `f"{self.notification.title} - {', '.join(self.to)}"`.
   - Done when `EmailNotification` enforces all validation rules on `full_clean()`, `create()`, and `save()`.

3. Update `EmailNotificationQuerySet` in `django_spire/notification/email/querysets.py`
   - Override `bulk_create()` to invoke `obj.validate_recipients()` on every `EmailNotification` before writing (serves `HelpDeskTicketNotificationService` and downstream bulk creators).
   - Override `bulk_update()` to invoke `obj.validate_recipients()` when `fields` includes any of `to`, `cc`, `bcc`.
   - Add `by_to_email(self, email: str) -> QuerySet` for recipient lookups (serves downstream apps migrating off `filter(to_email_address=...)`).
   - Done when `test_querysets.py` verifies `bulk_create`/`bulk_update` validation and `by_to_email()`.

4. Add safe chunked backfill & cleanup migration `django_spire/notification/email/migrations/0004_...py`
   - `AddField`: add `to = models.JSONField(default=list, validators=[EmailListValidator(allow_empty=False)])`.
   - `AlterField`: update `cc`, `bcc`, `context_data` with `blank=True` and `EmailListValidator()`.
   - `RunPython(migrate_email_recipients, revert_email_recipients)` in 1,000-row chunks (`iterator(chunk_size=1000)` + `bulk_update`):
     - **Forward**: populate `to` from `to_email_address` (handling normal single emails, comma/semicolon-separated strings, stringified JSON/Python lists, and logging a warning without aborting on blank legacy rows). Normalize legacy `cc`/`bcc` rows stored as `{}`, `None`, or bare `str` into `list[str]`.
     - **Reverse**: restore `to_email_address` from `to[0][:254]` (logging a warning if `len(to) > 1`, or `''` if empty) so rollback to `0003` works cleanly.
   - `RemoveField`: drop `to_email_address`.
   - Done when `makemigrations --check --dry-run` reports no changes, `migrate` applies cleanly on PostgreSQL, and `test_migrations.py` verifies forward conversion on every legacy shape plus rollback to `0003`.

5. Update `EmailHelper` & `SendGridEmailHelper` in `django_spire/notification/email/helper.py`
   - Read `email.to`, `email.cc`, and `email.bcc` (keeping defensive normalization for legacy/raw-SQL rows).
   - Set `self.template_data['to'] = ', '.join(self.to)` to stay backwards-compatible with existing SendGrid dynamic templates.
   - Done when `django_spire/notification/email/tests/test_helper.py` passes for single/multiple `to`, `cc`, `bcc`, and string-formatted `template_data['to']`.

6. Update `EmailNotificationAdmin` and admin smoke test factory
   - `django_spire/notification/email/admin.py`: display formatted `to` recipients in `list_display` and set `search_fields = ('id', 'to')`.
   - `django_spire/contrib/admin/tests/factories.py`: detect `EmailListValidator` on `JSONField`s and seed `[f'seed{index}@example.com']` when `allow_empty=False` and `[]` when `allow_empty=True` so `AdminSeedCoverageTests` stays green.
   - Done when `just test-app django_spire/contrib/admin` passes all changelist, search, form, query-count, and seed-coverage tests.

7. Update internal Spire callers and `test_project`
   - `django_spire/help_desk/services/notification_service.py`: pass `to=[settings.DEVELOPMENT_EMAIL if settings.DEBUG else user.email]` (raising `HelpDeskNotificationRecipientMissingEmailError` if empty).
   - `test_project/app/notification/forms.py`: parse comma-separated `email` input into `to=[...]` for create and update.
   - `test_project/templates/notification/item/list_item.html` and `test_project/templates/notification/modal/process_modal.html`: render `notification.email.to|join:', '`.
   - Done when `just test-app django_spire/help_desk` passes and `test_project` form/templates use `to`.

8. Update tests, documentation, changelog & verify
   - Update `django_spire/notification/email/tests/factories.py`, `test_models.py`, `test_querysets.py`, and `django_spire/help_desk/tests/test_services/test_notification_service.py`.
   - Add `test_validators.py`, `test_helper.py`, and `test_migrations.py`.
   - Update `docs/app_guides/notification/email_notifications.md` with `to` examples and field table.
   - Add a `v0`/`v1` downstream app upgrade checklist to `docs/changelog/changelog.md`.
   - Run completion tests and ruff checks.
   - Done when all test suites, migration checks, and `ruff` checks pass with zero errors.

## Completion Test

```bash
just test-app django_spire/notification
just test-app django_spire/help_desk
just test-app django_spire/contrib/admin
just python ./manage.py makemigrations --check --dry-run
just migrate
.venv/bin/ruff check django_spire/notification/email django_spire/help_desk django_spire/contrib/admin/tests/factories.py test_project/app/notification
.venv/bin/ruff format --check django_spire/notification/email django_spire/help_desk django_spire/contrib/admin/tests/factories.py test_project/app/notification
```

## Completion Result

Observed 2026-11-27:

- `just test-app django_spire/notification` (PostgreSQL 16) → **241 passed in 7.54s**
- `just test-app django_spire/help_desk` (PostgreSQL 16) → **74 passed in 4.57s**
- `just test-app django_spire/contrib/admin` (PostgreSQL 16) → **30 passed in 18.12s** (changelist, search, add/change forms, seed coverage, system checks, query count)
- `just python -m pytest django_spire/notification django_spire/help_desk django_spire/contrib/admin -n 0 --ds=test_project.sqlite_settings` → **345 passed, 4 deselected in 32.52s**
- `just python ./manage.py makemigrations --check --dry-run` → **No changes detected**
- Live migration round-trip (`0003` → legacy rows → `0004` → `0003` → `0004`) → **OK on both PostgreSQL 16 and SQLite**
- `.venv/bin/ruff check` across all touched Python files → **All checks passed!**
- `.venv/bin/ruff format --check` across all 11 touched/added files in `django_spire/notification/email/` → **11 files already formatted**

## Deviations

1. Switched from two-phase deprecation to single-step removal of `to_email_address`
   - What: Removed `to_email_address` inside migration `0004` right after chunked backfill into `to`, dropping the temporary Phase 1/Phase 2 deprecation shim and keeping `to` strictly non-empty (`blank=False`, `allow_empty=False`).
   - Why: User confirmed cleaning up `to_email_address` in one step; `v0.32.13` and `v1.7.0` share identical `0001`–`0003` migrations so `0004` safely migrates `v0` databases directly, while giving loud feedback during `v0 → v1` code upgrades and avoiding lingering deprecated schema/sync complexity.
2. Added `blank=True` to `template_id`, added `EmailNotificationQuerySet.update()` validation, and added pre-removal `AlterField(to_email_address, default='')` in `0004`
   - What: Marked `template_id` as `blank=True`, validated recipient kwargs on queryset `.update()`, and gave `to_email_address` a `default=''` right before `RunPython` / `RemoveField` in migration `0004`.
   - Why: Without `blank=True` on `template_id`, `full_clean()` fails on its default `''`; `.update(to=...)` would otherwise bypass validation; and without `default=''` prior to `RemoveField`, reversing `0004 → 0003` on a non-empty PostgreSQL table fails `ADD COLUMN ... NOT NULL`.
3. Booted local test PostgreSQL container and avoided reformatting unrelated lines outside `django_spire/notification/email/`
   - What: Started `docker compose -f test_project/docker-compose.test.yml up -d --wait` for PostgreSQL tests, and ran `ruff format` only on `django_spire/notification/email/` files while keeping all touched files clean under `ruff check`.
   - Why: Test Postgres on port 5439 was not running initially, and pre-existing files outside `notification/email` (`factories.py`, `notification_service.py`, `forms.py`) have unrelated formatting diffs under `ruff 0.17.6`.
