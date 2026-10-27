# Unique usernames in UserSeeder

Developer: Nathan Johnson (nathanj@stratusadv.com)
Status: Executed
Date: 2026-10-23-18-12

## End State

`UserSeeder` (django_spire/auth/seeding/seeder.py) seeds `User` rows whose `username` is unique within the batch, against pre-existing database rows, and across `reseed_database` batches, with a non-AI test proving each property.

## Observable Concern

The seeding bot generated every non-LLM field before the LLM fields, so a field whose value depends on an LLM-generated field (username derived from the LLM email) could never see that value; the fix had to preserve the pinned direct-call contract of `_process_non_llm_fields` while reordering generation into pre/llm/post passes.

## Current State

- Task 1 (executed, same day) shipped `Seeder.unique(...)` / `UniqueFieldSeed`: opt-in, DB-aware (snapshot via `_default_manager.values_list` at the `seed_index == -1` init), RLock-protected check-and-add, `is_cache_unsafe` disables the seed cache. Doc: `.backplan/2026-10-23-16-34-unique-seeder-fields.md`.
- `UserSeeder` set `username` in `__post_seed__` to the LLM email with no uniqueness guarantee; `AuthUser` (proxy) and `User` are the same table.
- `FieldSeedingBot.process` ran all non-LLM fields first, then LLM fields; `_process_non_llm_fields` is a staticmethod pinned by 5 direct-call tests in `tests/test_bots/test_field_seeding_bot.py`.
- `HelpDeskTicketSeeder` declared its LLM field first, so a naive "always LLM last" reorder would have emptied its LLM prompt context.
- Row generation runs in parallel on dandy's shared `ThreadPoolExecutor`; LLM mocking in non-AI tests goes through `dandy.llm.service.LlmService.prompt_to_intel`.

## Plan

1. Reorder the bot into a single forward pass
   - `_split_fields_around_llm` partitions `fields_seeds` into pre/llm/post by declaration order; pre fields fill the row, one LLM call fills the LLM fields (prompt context = pre row values), post fields run with the full row including LLM values.
   - Done when the 5 pinned `_process_non_llm_fields` tests and all non-AI bot tests pass unchanged.
2. Point `UserSeeder.username` at the unique seed
   - `fields_seeds['username'] = Seeder.unique(lambda row: row['email'])` after `'email'`; delete `__post_seed__`.
   - Done when a mocked-LLM `UserSeeder(count=N).seed_database()` yields N distinct usernames.
3. Audit LLM-context regressions
   - Reorder `HelpDeskTicketSeeder` so its LLM `description` is last (context keeps purpose/priority/status/created_by/created_datetime); all other production LLM seeders already declared LLM last.
   - Done when the only reorder needed is help_desk.
4. Add non-AI tests
   - Bot: LLM prompt includes pre-LLM values; post-LLM `UniqueFieldSeed(lambda row: row['email'])` sees the LLM value and dedupes `x`, `x-2`, `x-3` across rows (mock `LlmService.prompt_to_intel`).
   - UserSeeder: batch uniqueness, username == seeded email, uniqueness against a pre-created row (suffixed `-2`...), reseed stays unique.
   - Done when both files pass serial and under xdist.
5. Lint/format parity
   - Zero new ruff findings vs the Task 1 working-tree state; touched files format-clean (pre-existing dirt in `test_field_seeding_bot.py` left untouched, matching the Task 1 rule).
   - Done when `ruff check`/`ruff format --check` on touched files show nothing new.

## Completion Test

```bash
just test-app django_spire/contrib/seeding
just test-app django_spire/auth
just test
ruff check django_spire/contrib/seeding django_spire/metric django_spire/auth test_project/app/help_desk
```

Observed (2026-10-23 18:1x):

- seeding suite: `428 passed in 5.57s` (425 baseline + 3 bot tests)
- auth suite: `736 passed in 8.35s` (includes the 4 new UserSeeder tests)
- full suite: `19 failed, 4769 passed, 2 warnings, 4 subtests passed in 44.29s` - all 19 failures are the pre-existing `django_spire/core/components` test_form/test_scroll `Glue.Sequence` AttributeError set, identical to the Task 1 baseline (4762 passed then; +7 = the new tests)
- ruff: every Task 2-touched file is finding-free except `field_seeding_bot.py:106` N806, which exists verbatim at HEAD (pre-existing); `ruff format --check` clean on all new/touched code (the test-bots file's pre-existing unformatted lines were dirty at HEAD and left untouched)

## Deviations

1. Doc written retroactively; no pre-execution approval
   - What: This doc was written after execution began; the plan was not presented for approval beforehand.
   - Why: The request ("when we are seeding users the username must be unique can you apply the unique seed fix") directly extended the executed Task 1 by naming the exact mechanism to apply, and the session started executing immediately. The goal is stated here as derived from the request, flagged as assumed per the headless rule.
2. Bot fix scoped to declaration-order passes instead of "LLM always last"
   - What: LLM fields are processed in a single middle pass split by declaration order (pre/llm/post), rather than moved to the end unconditionally.
   - Why: It preserves each seeder's declared prompt context (fields before an LLM field remain context; only `HelpDeskTicketSeeder` needed a reorder) while making fields declared after an LLM field able to consume LLM values, which is the property `UserSeeder.username` needs.
