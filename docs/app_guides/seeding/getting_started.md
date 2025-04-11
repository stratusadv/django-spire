from django_spire.seeding import DjangoModelSeeder

# Getting Started

Let’s make your database feel alive!
This module helps you quickly populate Django models with meaningful, contextual data — without tedious boilerplate or repetitive scripts.

---

## Example Model

```python
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

## Controlling Defaults with `default_to`

By default, the system will fill any missing fields using a Large Language Model (LLM). But you can customize this behavior using the `default_to` class variable on your `ModelSeeding` subclass.

```python
from django_spire.seeding import DjangoModelSeeder

class ProductSeeder(DjangoModelSeeder):
    model_class = Product
    default_to = "llm"  # Options: 'llm', 'faker', 'included'
```

### Available Options

| `default_to` Value | What It Does                                                                 |
|--------------------|------------------------------------------------------------------------------|
| `"llm"` *(default)*     | Fills any unspecified fields using LLM-generated content                |
| `"faker"`               | Fills unspecified fields using faker-based defaults                     |
| `"included"`            | Only seeds the fields you explicitly define in the `fields` dictionary  |

---

## Basic Usage (LLM Defaults)

If you don’t define any fields, the system defaults to using LLMs for all fields (unless excluded):

```python
from django_spire.seeding import DjangoModelSeeder

class ProductSeeder(DjangoModelSeeder):
    model_class = Product
    fields = {
        "id": "exclude"
    }
 
ProductSeeder.seed(count=5) # Initialized model objects

# or

ProductSeeder.seed_database(count=5) # Insert objects into the database
```

> This is ideal for prototyping, testing, or generating rich placeholder content fast.

---

## Advanced Usage (All Field Types)

Use a mix of `faker`, `llm`, `static`, `callable`, and `custom` seed types for full control:

```python
import random
from django.utils import timezone

supplier_ids = [101, 102, 103, 104, 105]

class ProductSeeder(ModelSeeding):
    model_class = Product
    fields = {
        "id": "exclude",
        "name": ("faker", "word"),
        "description": ("llm", "Describe this product for a sales catalog."),
        "price": ("faker", "pydecimal", {"left_digits": 2, "right_digits": 2, "positive": True}),
        "in_stock": True,
        "created_at": ("faker", "date_time_between", {"start_date": "-30d", "end_date": "now"}),
        "updated_at": lambda: timezone.now(),
        "supplier_id": ("custom", "in_order", {"values": supplier_ids})
    }


ProductSeeder.seed_database(count=5)
```

> This gives you total control over how each field is generated for testing or development environments.

---

## Overriding Fields

You can override fields on any call to `.seed()` or `.seed_database()`:

```python
ProductSeeder.seed(
    count=1,
    fields={"in_stock": ("static", False)}
)
```

This is useful for:

- Creating edge-case records
- Seeding specific rules
- Overriding random behavior

---

## Full Database Seeding

```python
ProductSeeder.seed_database(count=100)
```

This will generate and insert 100 Product instances directly into your database.

---

## Supported Field Types

This module supports five field types to control how data is seeded:

### Faker

Use `faker` when you want realistic-looking data like names, addresses, dates, and numbers.

```python
"name": ("faker", "name")
"created_at": ("faker", "date_time_between", {"start_date": "-30d", "end_date": "now"})
```

**Common Faker Methods**

- `name`
- `word`
- `email`
- `date_time_between` (with `start_date`, `end_date`)
- `pydecimal` (with `left_digits`, `right_digits`, `positive`)

---

### LLM

Use `llm` to generate rich, human-like content based on a prompt. Great for descriptions, summaries, etc.

```python
"description": ("llm", "Describe this product for a catalog.")
```

If you don’t provide a field type, the system defaults to `llm` unless excluded — unless you set `default_to = "included"`.

---

### Static

Use `static` when you want the same value every time.

```python
"in_stock": ("static", True)
```

Or simply pass the value directly:

```python
"in_stock": True
```

Great for controlled values like feature flags or known test conditions.

---

### Callable

Use `callable` for dynamic behavior like random logic, timestamps, or context-aware generation.

```python
"updated_at": ("callable", lambda: timezone.now())
```

Or simply pass the function directly:

```python
"updated_at": lambda: timezone.now()
```

Callables are evaluated at runtime and must return the field's expected value.

---

### Custom

Use `custom` when you want to reference a reusable method inside the seeding system.
This is especially useful for indexing ordered values or setting foreign keys.

```python
"supplier_id": ("custom", "in_order", {"values": [101, 102, 103]})
```

This calls the built-in `in_order` method, which assigns values from the list one by one based on row index.

#### Built-in Custom Methods

| Method Name | Parameters           | Use Case                                           |
|-------------|----------------------|----------------------------------------------------|
| `in_order`  | `values: list`, `index` (auto-injected) | Assigns values sequentially by row — great for linking foreign keys like `user_id`, `supplier_id`, etc. |

---

Each type works independently or combined with others. Fields not declared in `fields` will default to `llm` or `faker` — unless `default_to` is set to `"included"`.