# Seeding: Getting Started

> **Purpose:** build a working seeder for a Django model with the current `Seeder` API — from a minimal example to full per-field control.

---

## Example Model

```python
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    created_datetime = models.DateTimeField(auto_now_add=True)
```

---

## A Minimal Seeder

Subclass `Seeder`, set `model_class`, and define `fields_seeds` for every field (use `Seeder.exclude()` for auto-managed ones):

```python
from django_spire.contrib.seeding import Seeder


class ProductSeeder(Seeder):
    model_class = Product

    fields_seeds = {
        'id': Seeder.exclude(),
        'name': Seeder.fake.sentence(3),
        'description': Seeder.llm(str, 'A short product description for a sales catalog.'),
        'price': Seeder.random.int(1, 500),
        'in_stock': Seeder.static(True),
        'supplier_id': Seeder.model.random_foreign_key(Supplier),
    }
```

`fields_seeds` is required on every seeder subclass — the class validates it at definition time.

---

## Running a Seeder

Instantiate with a count and call the output method you need:

```python
seeder = ProductSeeder(count=100)

seeder.seed_database()        # bulk_create 100 rows, returns the queryset
seeder.to_model_instances()   # 100 unsaved model instances
seeder.to_list_of_dicts()     # 100 plain dicts
```

Or re-seed (reset + seed) in one call:

```python
seeder.reseed_database(count=50)
```

Check the generated rows after seeding:

```python
products = seeder.queryset  # Product.objects.filter(pk__in=seeded_ids)
```

---

## LLM-Generated Fields

Use `Seeder.llm(field_type, prompt)` for rich, contextual text. The `field_type` constrains the generated output:

```python
'name': Seeder.llm(str, 'A name for a product in a grocery store catalog.'),
```

---

## Foreign Keys

Point fields at real instances instead of random integers:

```python
'supplier_id': Seeder.model.random_foreign_key(Supplier),           # any instance
'supplier_id': Seeder.model.random_queryset_foreign_key(            # filtered
    Supplier.objects.active()
),
'supplier_id': Seeder.model.ordered_foreign_key(Supplier),          # sequential (wraps around)
'status': Seeder.model.ordered_field_choice(ProductStatusChoices),  # rotate choices in order
'status': Seeder.model.random_field_choice(ProductStatusChoices),   # random choice
```

---

## Deterministic & Random Value Helpers

```python
# Rotates through a custom list per row (wrap=True cycles instead of raising)
'badge': Seeder.ordered.choice(['bronze', 'silver', 'gold']),

# Ascending datetime per row: start + index * step
'published_at': Seeder.ordered.datetime(start, step=timedelta(hours=1)),

# Sequential index values
'sort_order': Seeder.index(index_start=0, index_step=1),

# Random values
'rating': Seeder.random.int(1, 5),
'weight': Seeder.random.float(0.5, 10.0),
'tag': Seeder.random.choice(['sale', 'new', 'clearance']),
```

---

## Custom Callables & Files

Any callable works via `Seeder.custom.callable`:

```python
'updated_at': Seeder.custom.callable(lambda: timezone.now()),
```

File fields:

```python
'attachment': Seeder.file(upload_to='product_attachments/'),
```

---

## Mutating Default Generation

`Seeder.mutate` wraps another field seed and changes its behaviour — handy for generating edge cases:

```python
'name': Seeder.mutate.corrupt(Seeder.fake.sentence(3)),   # corrupted data
'name': Seeder.mutate.nullable(Seeder.fake.sentence(3)),  # randomly nullified
'name': Seeder.mutate.value(Seeder.fake.sentence(3), 'Fixed name')  # forced value
```

---

## Post-Seed Hooks

Override the class hooks to fix up cross-field or cross-model invariants after seeding:

```python
class EntrySeeder(Seeder):
    model_class = Entry

    fields_seeds = {
        'id': Seeder.exclude(),
        'name': Seeder.llm(str, 'A name for a document in a company knowledge base.'),
    }

    def __post_seed_database__(self) -> None:
        # runs after rows are saved — e.g. link related records
        for entry in self.queryset:
            entry.services.tag.process_and_set_tags()
```

`__post_seed__` runs after in-memory seeding; `__post_seed_database__` runs after the `bulk_create`.

---

## Inspecting Run Stats

```python
print(ProductSeeder.meta)          # per-seeder stats
ProductSeeder.print_meta_overview()
```
