# Django Seeding Module

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

# 5 null objects
products = seeder.generate_model_objects(count=5)

# Inserts 5 records
products = seeder.seed_database(count=5)

```

> ✅ This is ideal for prototyping, testing, or generating rich placeholder content fast.

---

## 🔧 Advanced Usage (All Field Types)

Use a mix of `faker`, `llm`, `static`, and `callable` seed types for full control:

```python
import random
from django.utils import timezone
from your_module import ModelSeeding
from your_app.models import Product

seeder = ModelSeeding(
    model_class=Product,
    exclude_fields=["id"],
    fields={
        "name": ("faker", "word"),
        "description": ("llm", "Describe this product for a sales catalog."),
        "price": ("faker", "pydecimal", {"left_digits": 2, "right_digits": 2, "positive": True}),
        "in_stock": ("static", True),
        "created_at": ("faker", "date_time_between", {"start_date": "-30d", "end_date": "now"}),
        "updated_at": ("callable", lambda: random.choice([None, timezone.now()])),
    }
)

products = seeder.generate_model_objects(count=10)
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

- [Faker Seeding](faker.md)
- [Faker Documentation](https://faker.readthedocs.io/en/master/)

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

Use `callable` for dynamic or computed values at runtime.

```python
"updated_at": ("callable", lambda: timezone.now())
```

Or simply pass the function directly:

```python
"updated_at": lambda: timezone.now()
```

This is great for timestamps, randomized logic, or values that depend on other runtime data.
Callables are evaluated at runtime and must return the field's expected value.

---

Each type works independently or combined with others. Fields not declared in `fields` default to `llm` unless excluded.

