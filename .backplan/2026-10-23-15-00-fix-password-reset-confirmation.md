# Fix the password reset confirmation page

Developer: Chase Mossing (chasem@stratusadv.com)
Status: Executed
Date: 2026-10-23-15-00

## End State

On `v1.4.0/base`, the page an emailed reset link opens (`django_spire:auth:admin:password_reset_confirmation`) renders, shows Django's errors, sets the new password, and tells a visitor whose link is used or expired to request a new one; `django_spire/form/delete_form.html` renders and still posts `should_delete=true`; the allauth-era pages (`password_reset_key_form`, `password_reset_key_form_done`, `password_set_form`) are gone with their views and URLs; and `django_spire/auth/tests/test_views.py` and a core template test prove each of these.

## Observable Concern

The confirmation page is a plain Django form post, and Django's `PasswordResetConfirmView` swaps the token in the emailed link for one in the session and redirects to `.../set-password/` before the form shows. A test that GETs the emailed link without following that redirect sees only a 302, and one that posts to the emailed URL instead of the redirected one is refused, so the tests must follow the flow as a browser does or a passing test could prove nothing about the form.

## Current State

- Repository
  - `django-spire` on `v1.4.0/base` at `62c9fe64`, level with `origin/v1.4.0/base`. `.run/Run Tests.run.xml` has an unrelated local change, left alone. No `.backplan/` folder yet.
  - Work lands on `v1.4.0/base` by direct commits (`62c9fe64`, `3db63a6a`); no PRs into it.
  - `pyproject.toml` pins `django-glue==1.3.0`; the venv was stale (Glue 1.1.1) and `uv run --frozen` synced it.
  - Tests: `DANDY_SETTINGS_MODULE=test_project.dandy_settings uv run --frozen pytest django_spire/auth django_spire/core` → 1201 passed (settings `test_project.test_settings` from `addopts`).
- The bug
  - `password_reset_confirmation_page.html` builds `new GlueCharField('new_password1', ...)` in `x-data` and includes `django_spire/glue/form/field/char/password_field.html` with `glue_field='new_password1'`. The include extends `django_spire/glue/form/widget/widget.html`, which runs `glue_field|glue_field_metadata_path`; the filter does `owner, field_name = value.rsplit('.', 1)` and raises `ValueError` on a name with no owner. Reproduced on this branch through the view with a made-up link, and on Spire 1.2.2 with Glue 1.2.2.
  - The template has no `{% if validlink %}`, so any link, valid or not, renders the broken fields; it never shows the form's errors.
  - Since `d21f059a` (2026-08-18, "refactor glue form fields"), in every release from 1.1.0 to 1.3.0 and on `v1.4.0/base`.
  - `django_spire/form/delete_form.html` includes `django_spire/glue/form/field/choice/field.html` with `glue_field='should_delete'`, same crash. Only `form/card/delete_form_card.html` includes it, and nothing in Spire, Stratus Portal, Showcase, Moonlite or Profitly uses that card. `DeleteConfirmationForm.should_delete` is a `BooleanField(required=False, initial=False)`; the template posts `true`.
  - `password_reset_key_form_page.html` and `password_set_form_page.html` have the same crash. With `password_reset_key_done_page.html` they are allauth leftovers: they use `token_fail` and link to URL names that do not exist (`user_account_reset_password`, `user_account_login`). Their views (`PasswordResetKeyForm`, `PasswordResetKeyFormDone`, `PasswordSetForm` in `auth/views/admin_views.py`) are bare `PasswordResetView` subclasses, mounted in `auth/urls/admin_urls.py`; nothing links to them. The only other mention is a commented-out test in `auth/tests/test_url_endpoints.py` naming a namespace that also does not exist.
- The pattern to follow
  - The working auth pages are plain HTML inputs in a `method="post"` form with `{% csrf_token %}`: `password_reset_page.html`, `password_change_page.html` (with an Alpine match check) and `auth/form/login_form.html`, which names inputs from the bound form (`form.<field>.name`, `id_for_label`, `label`) and lists `form.<field>.errors`.
  - Django's confirmation context: `validlink`, and `form` (a `SetPasswordForm` with `new_password1`, `new_password2`) only when the link is valid.
- Docs and tests
  - `docs/changelog/changelog.md` has `## v1.4.0 - Unreleased` with `### Breaking`, `### Added` sections.
  - `django_spire/auth/tests/test_views.py` covers the reset request (`PasswordResetViewTestCase`) but never opens the confirmation page; there are no template render tests for `delete_form.html`.
- Also on the old API, left out of this fix: `docs/components/templates/form.html` and five `test_project/templates/file/card/*` templates. They are not shipped in the package.

## Plan

1. Branch
   - `git switch -c chasem/password-reset-confirmation` from `v1.4.0/base`.
   - Done when `git branch --show-current` prints it at `62c9fe64`.
2. Tests first
   - `PasswordResetConfirmationViewTestCase` in `django_spire/auth/tests/test_views.py`: a valid emailed link (taken from `mail.outbox`) shows the form after Django's redirect; posting matching passwords redirects to `password_reset_complete` and the new password authenticates while the old one doesn't; mismatched passwords re-render with `new_password2`'s error and leave the password unchanged; a used link, and a made-up one, render 200 with the "request a new one" message and no form.
   - A render test for `django_spire/form/delete_form.html` in `django_spire/core/tests/`, asserting it renders with the description and a hidden `should_delete` input valued `true`.
   - Done when the new tests fail on the current templates with the `ValueError`.
3. Rewrite the confirmation page
   - Plain inputs named from `form.new_password1` and `form.new_password2`, labels and errors as in `login_form.html`, and `form.non_field_errors`; inside `{% if validlink %}`, with an `{% else %}` that says the link is used or expired and links to `password_reset`.
   - Done when step 2's confirmation tests pass.
4. Rewrite the delete form
   - A hidden `<input type="hidden" name="should_delete" value="true">` in place of the Glue field; nothing else changes.
   - Done when step 2's delete form test passes.
5. Remove the allauth leftovers
   - Delete `password_reset_key_form_page.html`, `password_reset_key_done_page.html` and `password_set_form_page.html` (`git rm`), the three views, and their three URLs.
   - Done when `git grep` finds no `password_reset_key` or `password_set_form` outside the commented-out test, and `reverse` of the remaining auth URLs still works.
6. Changelog
   - Under v1.4.0: a Fixed entry for the confirmation page and the delete form, and a Breaking entry for the removed URLs and templates.
   - Done when the entries read correctly.
7. Full check
   - Auth and core suites, and ruff on the touched Python files. The test project sends email through SendGrid (`test_project/base_settings.py`), so the reset flow is walked in a browser by Profitly's PROF-13 once it picks up this fix, not here.
   - Done when the completion test below passes.

## Completion Test

- `DANDY_SETTINGS_MODULE=test_project.dandy_settings uv run --frozen pytest django_spire/auth django_spire/core` passes, including the new confirmation and delete form tests.
- `ruff check` on `django_spire/auth/views/admin_views.py`, `django_spire/auth/urls/admin_urls.py` and the new tests reports nothing new.
- `git grep -n "password_reset_key\|password_set_form" -- django_spire` prints only the commented-out lines in `test_url_endpoints.py`.

## Deviations

1. A browser test of the reset flow in Spire
   - What: an e2e test (`pytest -m e2e`, Playwright with limelight's `demo_start`, like `test_side_navigation_e2e.py`) requests a reset in a real browser, takes the link from `mail.outbox`, sets a new password, logs in with it, and opens the link again to see it refused. The completion test gains `pytest -m e2e` on that file. Step 7's note that the flow is walked only by Profitly no longer holds; Profitly's walk still happens for PROF-13.
   - Why: the user asked for a browser-testing workflow. Under the test settings the live server keeps email in memory, so SendGrid is no obstacle, and the test stays as a guard against templates drifting from the Glue API again.
2. The iOS install prompt's default icon points at a file Spire ships
   - What: `auth/element/ios_app_install_element.html`'s `app_icon` default changes from `django_spire/favicons/android-chrome-192x192.png`, which does not exist, to `android-icon-192x192.png`, which does. A changelog Fixes entry records it.
   - Why: the browser test passed, then limelight's JavaScript error guard failed it on the 404 for that image, which every Spire auth page requests. Profitly, Stratus Portal and Moonlite override the element with their own icon, so only Spire's default was broken. Fixing the path keeps the guard honest; marking the error as expected would hide it.
