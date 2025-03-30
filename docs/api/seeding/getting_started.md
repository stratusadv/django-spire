# Getting Started

Let’s make your database feel alive! 🧪
This module helps you quickly populate Django models with meaningful, contextual data — without tedious boilerplate or repetitive scripts.

---

## 🧪 Example Model

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

## 🚀 Basic Usage (LLM Defaults)

If you don’t define any fields, the system defaults to using LLMs for all fields (unless excluded):

```python
seeder = ModelSeeding(
    model_class=Product,
    exclude_fields=["id"]
)

products = seeder.generate_model_objects(count=5)

# Or insert directly
seeder.seed_database(count=5)
```

> ✅ This is ideal for prototyping, testing, or generating rich placeholder content fast.

---

## 🔧 Advanced Usage (All Field Types)

Use a mix of `faker`, `llm`, `static`, `callable`, and `custom` seed types for full control:

```python
import random
from django.utils import timezone
from your_module import ModelSeeding
from your_app.models import Product

supplier_ids = [101, 102, 103, 104, 105]

seeder = ModelSeeding(
    model_class=Product,
    exclude_fields=["id"],
    fields={
        "name": ("faker", "word"),
        "description": ("llm", "Describe this product for a sales catalog."),
        "price": ("faker", "pydecimal", {"left_digits": 2, "right_digits": 2, "positive": True}),
        "in_stock": True,
        "created_at": ("faker", "date_time_between", {"start_date": "-30d", "end_date": "now"}),
        "updated_at": lambda: timezone.now(),
        "supplier_id": ("custom", "in_order", {"values": supplier_ids})
    }
)

products = seeder.generate_model_objects(count=5)
Product.objects.bulk_create(products)
```

> 🧩 This gives you total control over how each field is generated for testing or development environments.

---

## 🎯 Overriding Fields

You can override fields on any call to `.generate_model_objects()` or `.seed_database()`:

```python
seeder.generate_model_objects(
    count=1,
    fields={"in_stock": ("static", False)}
)
```

This is useful for:

- Creating edge-case records
- Seeding specific rules
- Overriding random behavior

---

## 🔄 Full Database Seeding

```python
seeder.seed_database(count=100)
```

This will generate and insert 100 Product instances directly into your database.

---

## 🧰 Supported Field Types

This module supports four field types to control how data is seeded:

### 🧪 Faker

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

### 🧠 LLM

Use `llm` to generate rich, human-like content based on a prompt. Great for descriptions, summaries, etc.

```python
"description": ("llm", "Describe this product for a catalog.")
```

If you don’t provide a field type, the system defaults to `llm` unless excluded.

---

### 📌 Static

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

### 🧮 Callable

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

### 🛠️ Custom

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

Each type works independently or combined with others. Fields not declared in `fields` default to `llm` unless excluded.

