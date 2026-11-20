# Track API key last-used on successful auth — 2026-11-19-11-38

Developer: Brian Park (brianp@stratusadv.com)
Status: Executed
Date: 2026-11-19-11-38

## End State

`ApiAccess` has a `last_used_datetime` column that is stamped (at most once per
hour) whenever a key authenticates successfully, and the value renders as
"Last Used" — the timestamp, or "Never used" when null — on the API key list
item, the detail card, and the admin list.

## Observable Concern

"Which key was used" is known only transiently, in memory, inside the request;
Django keeps no record after the response, so usage must be persisted at the
one moment it is known — the `ApiKeySecurity` success path. Reusing
`Activity`/`HistoryEvent` was rejected: `Activity.user` is a non-null FK and
some keys have no user, and neither fires on auth (auth never saves the row).
The stamp must therefore bypass `HistoryModelMixin.save()` (a queryset
`.update()`) so it records nothing in the history/activity feed.

## Current State

Verified 2026-11-19 against the working tree:

- `django_spire/api/models.py:11` `ApiAccess(ActivityMixin, HistoryModelMixin)`;
  `set_key_and_save()` hashes via `tools.hash_string` (HMAC-SHA256 of SECRET_KEY).
- `api/auth/security.py`: `authenticate` reads the key (`get_by_key_or_none`),
  checks permission/user perms; **every** success returns through
  `_authorize_request()` (security.py:50); all failures return `False` first. It
  never `.save()`s the row, so usage leaves no DB trace.
- `api/views/page_views.py:23` list view passes `ApiAccess.objects.active()
  .select_related('user')`.
- `access_item.html:48-51` has a broken duplicate "Created On" block referencing
  an empty `api_access.` token — reused here for "Last Used".
- `access_detail_card.html` ends after the "Created On" cell (line 33-36).
- `api/admin.py:16-18` `list_display`/`readonly_fields` have no usage field.
- Migrations: latest `0005` → new is `0006`.
- Settings defaults live in `django_spire/settings.py`, surfaced through
  `django_spire/conf.py`'s `settings` wrapper (verified: any default there is
  readable via `from django_spire.conf import settings`).
- Lint/format: venv `ruff` (`ruff.toml`). Test cmd: `just test-app api`.

## Plan

1. Model field + migration
   - Add `last_used_datetime = models.DateTimeField(null=True, blank=True,
     editable=False)` to `ApiAccess`. Generate `0006_apiaccess_last_used_datetime`.
   - done when `just make-migrations` emits `0006` and `just migrate` applies it.
2. Stamp on successful auth
   - In `_authorize_request()` before `return api_access`, throttled `.update()`
     (bypasses save → no history/activity; covers super-access path too):
     `ApiAccess.objects.filter(Q(pk=..) & (Q(last_used_datetime__isnull=True) |
     Q(last_used_datetime__lt=cutoff))).update(last_used_datetime=localtime())`,
     `cutoff = localtime() - timedelta(minutes=settings.DJANGO_SPIRE_API_KEY_LAST_USED_THROTTLE_MINUTES)`.
     Add imports `timedelta`, `Q`, `localtime`, `from django_spire.conf import settings`.
   - done when a valid-key request sets `last_used_datetime`, a second call within
     the hour leaves it unchanged, and a failed-key request leaves it null.
3. Setting
   - Add `DJANGO_SPIRE_API_KEY_LAST_USED_THROTTLE_MINUTES = 60` to
     `django_spire/settings.py`.
   - done when the value is readable via `django_spire.conf.settings`.
4. List item + detail card render
   - `access_item.html:48-51`: replace the broken duplicate block with a
     "Last Used" column showing
     `{{ api_access.last_used_datetime|date:'M d, Y g:i A'|default:'Never used' }}`.
   - `access_detail_card.html`: add a matching "Last Used" cell after Created On.
   - done when both templates render the timestamp and "Never used" for nulls.
5. Admin
   - `api/admin.py`: add `last_used_datetime` to `list_display` and `readonly_fields`.
   - done when the admin change list shows the column read-only.
6. Tests + verification
   - `test_security.py`: stamp on success; no move within throttle window;
     null on failed auth. `test_views/test_page_views.py`: list shows the stamped
     value.
   - Run `just test-app api`; `just make-migrations` → no changes; venv `ruff check`
     + `ruff format --check` on touched files.
   - done when all green and output captured.

## Completion Test

```bash
just test-app api
just make-migrations            # expect: No changes detected
just migrate
.venv/Scripts/ruff check django_spire/api django_spire/settings.py
.venv/Scripts/ruff format --check django_spire/api django_spire/settings.py
```

## Completion Result

Observed 2026-11-19:

- `just test-app django_spire/api` → **50 passed** (incl. the new
  `test_authenticate_stamps_last_used_datetime`,
  `test_authenticate_within_throttle_window_leaves_last_used_unchanged`,
  `test_authenticate_after_throttle_window_updates_last_used`,
  `test_failed_authenticate_does_not_stamp_last_used`,
  `test_access_list_view_shows_last_used_column`).
- `manage.py makemigrations --check --dry-run` → **No changes detected**.
- `just migrate` → `Applying django_spire_api.0006_apiaccess_last_used_datetime... OK`.
- `ruff check` on every file I authored/edited (security.py, settings.py,
  admin.py, models.py, test_security.py, test_page_views.py) → **All checks
  passed**.

## Deviations

1. Test Postgres had to be started before tests could run
   - What: `docker compose -f test_project/docker-compose.test.yml up -d` to bring
     up the test DB on port 5439 (test_settings default) before `just test-app`
     could connect — it was refusing connections.
   - Why: environment precondition, not a plan change; the suite never ran without it.
2. Pre-existing ruff findings in the api package left untouched
   - What: `ruff check`/`ruff format --check` report findings on lines I did not
     author (admin.py `has_add_permission` ARG002, search.py TC002/ARG002,
     form_views.py E501, page_views.py/navigation.py W292, plus pre-existing format
     diffs in security.py/models.py/test_security.py). Only my own added lines were
     made format-canonical (the `_record_use` cutoff and the test `stale` line
     collapsed to single lines).
   - Why: the venv ruff is newer than the repo baseline (AGENTS: newer ruff adds
     findings), and CI gates on `ruff check` lint, not `format --check`. The whole
     api package predates the current format settings; reformatting unrelated code
     is scope creep. Zero findings land on code this change authored.
3. Display format chosen as `'M d, Y g:i A'`
   - What: "show the time" rendered as `Nov 19, 2026 05:42 PM` in both the list
     item and detail card.
   - Why: user asked to "just show the time" with no badge; date + clock time
     satisfies "time" while staying readable.
