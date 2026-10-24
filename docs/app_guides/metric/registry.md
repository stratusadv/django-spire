The metric registry lets you declare your metric structure (domains, sub-domains, statistic groups, and statistics) in code, then sync it into the database with a single command instead of creating each row through the admin.

Key features include:
- One `Metric` subclass per application, declared with nested spec constructors.
- `manage.py metric_build` idempotently creates and syncs the structure.
- `--check` mode validates the structure for CI, exiting non-zero when it drifts.
- `record()` writes values against declared keys, local or to a remote Spire installation, without blocking the caller.

## Installation

Register your registry class in settings — a list of dotted paths to `Metric` subclasses:

```python title="settings.py"
DJANGO_SPIRE_METRIC_REGISTRY = [
    'myapp.metrics.StoreMetric',
]
```

For remote targets, name them here (falling back to `DJANGO_SPIRE_REMOTE_API_URL`/`DJANGO_SPIRE_REMOTE_API_KEY` for any name):

```python title="settings.py"
DJANGO_SPIRE_METRIC_REMOTE_TARGETS = {
    'central': {
        'url': 'https://metrics.example.com',
        'api_key': '...',
    },
}
```

## The `Metric` class

Subclass `Metric`, set `target` (defaults to `Metric.Target.LOCAL`), and declare your structure under `domains`:

```python title="myapp/metrics.py"
from django_spire.metric import Metric


class StoreMetric(Metric):
    domains = [
        Metric.Domain(
            'store',
            name='Store',
            description='Storefront sales and fulfillment metrics.',
            sub_domain_name='Channels',
            subdomains=[
                Metric.SubDomain('web', name='Web'),
                Metric.SubDomain('retail', name='Retail'),
            ],
            statistic_groups=[
                Metric.StatisticGroup(
                    'orders',
                    name='Orders',
                    statistics=[
                        Metric.Statistic('created', name='Orders created'),
                        Metric.Statistic('revenue', name='Order revenue', value_type='currency'),
                    ],
                ),
            ],
        ),
    ]
```

The first argument of every constructor is the **key** — a lowercase slug. The remaining spec fields mirror the model fields: `Domain` takes `name`, `description`, and `sub_domain_name`; `SubDomain` and `StatisticGroup` take `name` and `description`; `Statistic` takes `name`, and optionally `interval` (`daily`, `weekly`, `monthly`) and `value_type` (`number`, `currency`, `percentage`).

Specs are validated when the class is defined: a non-enum `target` or a `domains`/`subdomains`/`statistic_groups`/`statistics` entry that is not a spec raises `TypeError`; a `REMOTE` target without `remote_target`, empty `domains`, non-slug keys, `__` in a key, duplicate keys, unknown `interval`/`value_type`, and stored keys over 64 characters all raise `ValueError` immediately.

### The key contract

Stored keys are namespaced by their parents so the same local key can be reused under different domains:

| Spec | Stored key |
|------|------------|
| `store` | `store` |
| `web` under `store` | `store__web` |
| `orders` under `store` | `store__orders` |
| `created` under `store`/`orders` | `store__orders__created` |

These stored keys are the public contract for `record()`, `check()`, and the tracking middleware settings. Renaming a **name** in the spec is safe (the build updates it); changing a **key** after values have been recorded is destructive, because the statistic gets a new key and the old row (with its values) becomes an orphan.

A reference implementation lives in `test_project/app/metrics/metrics.py` (`StoreMetric`). A manual test page with clickable record buttons is at `/metrics/page/record_test/`, linked from the side navigation as "Metric Record Test" (see `test_project/app/metrics/views.py`).

## Building the structure

```bash
just metric-setup                             # dev shortcut for the build below
python manage.py metric_build              # build every registered registry
python manage.py metric_build --check      # validate only; exit 1 on drift
python manage.py metric_build --registry myapp.metrics.StoreMetric
```

The build walks each registry top-down and find-or-creates every level by key. It updates `name`/`description` (and `sub_domain_name`, `interval`, `value_type` when declared) when they drifted from the spec, never touches `is_active`/`is_deleted`, and prints `created`, `updated`, and `unchanged` counts. Rows that exist but are soft-deleted are reported as errors, not resurrected. After a build, rows that exist in the database but are declared in no registry are listed as orphans (warning only, never deleted).

`--check` performs the same walk without writing anything and exits non-zero when anything is missing. Run it in CI to gate deploys.

### Existing rows

Rows created through the admin before the registry existed get name-derived keys (for example `sales-web`) that usually do not match the spec's namespaced keys (`sales__web`). The first build creates the spec rows and lists the legacy rows as orphans; clean those up manually once the registry is authoritative.

## Checking and recording from code

```python
from myapp.metrics import StoreMetric

StoreMetric.check()
# BuildSummary(created=0, updated=0, unchanged=6, missing=[], errors=[])

worker = StoreMetric.record(
    'store', 'web', 'orders', 'created', reference=['order', 'created'], value=3
)
# Returns immediately; the write happens on a short-lived background thread.
# worker.join()  # wait for the write to finish (mainly useful in tests)
```

- `check()` queries the database for a local target, or probes the remote API (`GET {key}/total`) for a `REMOTE` target. A probe that fails — an HTTP error or a network error — is counted as missing, so a downed remote reports as drift instead of crashing the check.
- `record(domain_key, sub_domain_key, statistic_group_key, statistic_key, reference, value=1, *, source_model=None)` validates the keys against the declared spec synchronously (an unknown key or sub-domain raises `ValueError` immediately), then dispatches the write on a short-lived daemon thread and returns that thread. The `reference` is required and must be a list of strings — a bare string is rejected with `TypeError` — and the segments are joined with `:` for storage (e.g. `['order', 'created']` stores `order:created`). Pass a saved Django model instance as `source_model` to append `<app_label>.<model_name>:<pk>` to the stored reference (e.g. `order:created:myapp.task:7`). Write failures — a missing row in the database, a remote error — are logged and dropped, never raised, and the worker closes its own database connections before exiting. Callers normally ignore the returned thread; tests can `join()` it.
- `build()` on a `REMOTE` target raises an error — run `metric_build` on the remote installation to build its structure. Remote registries can still `record()` and `check()` against it.
