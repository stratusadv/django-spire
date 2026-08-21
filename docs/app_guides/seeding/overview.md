# Seeding Overview

> **Purpose:** seed Django models quickly with realistic, contextual data — for testing, demoing, and onboarding — without tedious boilerplate or repetitive scripts.

---

## How It Works

Seeders are subclasses of `django_spire.contrib.seeding.Seeder`. Each seeder declares its target model (`model_class`) and a `fields_seeds` dict mapping every field to a **field seed**:

| Field Seed | What It Does |
|---|---|
| `Seeder.fake.<faker>()` | Generates realistic fake data via the [faker](https://faker.readthedocs.io/en/master/) library (`sentence()`, `paragraph()`, `date_time_between()`, ...) |
| `Seeder.llm(field_type, prompt)` | Uses a large language model to generate rich, contextual content |
| `Seeder.static(value)` | Uses a fixed value for consistent results |
| `Seeder.custom.callable(fn, ...)` | Runs a function to generate custom dynamic values |
| `Seeder.model.<helper>(...)` | Model-aware generation — foreign keys to real instances, random/ordered field choices |
| `Seeder.ordered.<helper>(...)` | Deterministic per-row values (rotating choices, ascending datetimes) |
| `Seeder.random.<helper>(...)` | Random values (choices, ints, floats) |
| `Seeder.mutate.<helper>(...)` | Mutates the default generation for a field (corrupt, exclude, nullable, type, value) |
| `Seeder.exclude()` | Skip a field entirely (typically `id`) |
| `Seeder.file(upload_to)` | Generates a file upload |
| `Seeder.index(index_start, index_step)` | Sequential index values |

See [Getting Started](getting_started.md) for a full walkthrough and [Faker](faker.md) for field-to-faker defaults.

---

## Fast Rebuilds with Caching

Seed results are stored in a local cache so re-seeding the same count is instant on the next run. Enable/disable per seeder with the `cache_enabled` class variable; the cache name is derived from the seeder class name automatically:

```python
class TaskModelSeeder(Seeder):
    model_class = Task
    cache_enabled = True
```

Perfect for:

- Rapid development
- Restoring known states
- Testing edge cases

---

## Output Options

A seeder can produce data several ways:

| Method | Returns |
|---|---|
| `seed(count)` | Populates the seeder's internal seed list (no DB writes) |
| `seed_database(count)` | Seeds and `bulk_create`s the rows, returns the resulting `QuerySet` |
| `reseed_database(count)` | Resets then `seed_database`s |
| `to_list_of_dicts(count)` | Seeds as plain dicts |
| `to_model_instances(count)` | Seeds as unsaved model instances |
| `to_json(count)` | Seeds serialized as JSON |

Track run stats with `seeder.meta` and `Seeder.print_meta_overview()`.

---

## Next Steps

- [Getting Started](getting_started.md)
- [Faker Field Defaults](faker.md)
