# ruff cleanup seeding metric

Developer: Nathan Johnson (nathanj@stratusadv.com)
Status: Executed
Date: 2026-10-23-20-34

## End State
`ruff check django_spire/contrib/seeding django_spire/metric` reports 0 findings (156 at start), with the seeding and metric test suites still passing at their baseline counts (431 and 653).

## Observable Concern
`TC002` auto-fixes move `TYPE_CHECKING` imports; files that evaluate annotations at runtime (no `from __future__ import annotations`) can break on import or use. The metric suite imports every touched module, so a green metric run is the verification.

## Current State
- `ruff check django_spire/contrib/seeding django_spire/metric --output-format concise` reports **156** findings (full list captured at session start; per-rule: ANN* ~55, TC002 x15, F401 x14, E501 x13, PLC0415 x8, ARG* x26, SIM300 x3, F811 x3, F541 x3, plus one-offs: TD002/TD003/FIX002, N806, PT028 x2, A002, B904, DTZ001, FBT003 x2, DJ008 x2, TRY003/EM101 x2, RSE102, PT011, RUF100, RET505, W292).
- 24 findings have safe `--fix`; 29 more hidden behind `--unsafe-fixes` (not used).
- Baselines: seeding 431 passed, metric 653 passed, full suite 4779 passed / 19 pre-existing `core/components` Glue.Sequence failures.
- Repo-wide ruff is 1044 findings; out of scope for this task (reported, not fixed).
- 37 scoped files are `ruff format`-dirty at baseline; "ruff errors" means `ruff check` findings, so formatting is out of scope (noted in report).

## Plan
1. Safe auto-fixes
   - `ruff check --fix django_spire/contrib/seeding django_spire/metric` (no `--unsafe-fixes`): F401, F541, SIM300, RET505, RUF100, W292, TC002, safe F811.
   - Done when `ruff check` count drops below 156.
2. Validate auto-fixes
   - `just test-app django_spire/contrib/seeding` and `just test-app django_spire/metric`.
   - Done when 431 and 653 pass (watch for test-count changes from the F811 duplicate removal in `test_custom_helper.py` if it was auto-fixed).
3. Manual fixes, file by file
   - ANN*: add type annotations (~69 findings).
   - ARG001/ARG002: unused `request`/`seed_index` params renamed `_request`/`_seed_index` (positional callers unaffected), except django-ninja endpoint params in `metric/domain/statistic/api_v1.py`, where `request` is injected by name and must be kept/used appropriately (read first).
   - E501 x13: reformat long lines.
   - PLC0415 x8: move function-local imports to top level (check clashes: `test_full_integration.py` has a paired F811 `models` import).
   - F811: `seed/seed.py` duplicate `__eq__` (merge), `test_custom_helper.py` duplicate test (delete shadowed copy, keep test count flat).
   - PT028 x2: `signage/views/page_views.py` view named `test_*` renamed + its URL wiring.
   - TD002/TD003/FIX002: `seeder.py:35` TODO comment reworded as a plain note.
   - N806: `field_seeding_bot.py:106` local `FieldIntel` -> `field_intel`.
   - A002: `metric/report/report.py:159` arg `type` shadows builtin (grep callers first).
   - Remaining one-offs: B904, DTZ001, FBT003 x2, DJ008 x2, TRY003/EM101 x2, RSE102, PT011.
   - Done when `ruff check` on the two paths reports 0.
4. Re-verify
   - Re-run seeding + metric suites; `ruff format --check` on every manually edited file.
   - Done when suites green at baseline counts, edited files format-clean, scoped `ruff check` = 0.

## Completion Test
```
ruff check django_spire/contrib/seeding django_spire/metric
# -> All checks passed! (or "Found 0")
just test-app django_spire/contrib/seeding   # -> 431 passed
just test-app django_spire/metric            # -> 653 passed
```

## Deviations
1. TC002 fixes applied with `--unsafe-fixes --select TC002` (surgical, 10 files only)
   - What: The 15 TC002 moves are classified unsafe by ruff; after verifying every one of the 10 affected files has `from __future__ import annotations` and that neither django-glue's `Glue.attr` collector nor the core `Search` base introspect annotations at runtime, the targeted unsafe fix was applied instead of hand edits.
   - Why: ruff's own placement logic is authoritative for import ordering; the safety preconditions that make the fix unsafe-by-default were verified to hold.
2. django-ninja `request` params kept, not removed
   - What: The four endpoints in `metric/domain/statistic/api_v1.py` keep their (unused) `request: HttpRequest` parameter with `# noqa: ARG001` on the parameter line, instead of dropping the parameter.
   - Why: ninja detects the request parameter by the literal name `request` (`ninja/signature/details.py`) and calls the view as `view_func(request, **values)`; removing or renaming the parameter makes the positional `request` bind to the first real parameter (`record_value() got multiple values for argument 'statistic_key'`, 21 test failures observed).
3. DTZ001 fixed with stdlib `UTC`, dropping the `make_aware` wrapper
   - What: `test_corrupt_seed.py` now seeds `datetime(2026, 8, 14, 12, 30, tzinfo=UTC)` directly instead of `timezone.make_aware(datetime(...))`.
   - Why: Django 6's `make_aware` raises `ValueError` on an already-aware datetime, so simply adding `tzinfo` inside the wrapper was not viable; the test intent (an aware datetime through the chaos corruptor) is unchanged.
