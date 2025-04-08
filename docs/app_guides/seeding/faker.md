# 🧪 DjangoFieldToFakerData Developer Reference

This utility class generates fake data for Django model fields using the [`faker`](https://faker.readthedocs.io/en/master/) library. It supports optional **faker_method** to customize faker behavior on a per-field basis.

---

## 🚀 Getting Started

### 👩‍🍳 Example Django Model

```python
from django.db import models
from django.core.validators import MinValueValidator

class Recipe(models.Model):
    name = models.CharField(max_length=100)
    servings = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateField()
```

---

### 🔹 Simple Example (No Context)

```python
from django_spire.core.converters import fake_model_field_value

fake_name = fake_model_field_value(Recipe, 'name')
print(fake_name)
```

---

### 🔸 Advanced Example (With Context)

```python
# Generate a name using faker.name()
fake_name = fake_model_field_value(Recipe, 'name', faker_method='name')

# Generate a date in a custom range
fake_date = fake_model_field_value(Recipe, 'created_at', faker_method=('date_between', {'start_date': '-10d', 'end_date': 'today'}))
print(fake_date)
```

---

## 🔧 Supported Field Types & Faker Context Methods

| Django Field Type       | Faker Method (for faker_method)     | Example Context Tuple                                      | Faker Method `kwargs`                                      |
|-------------------------|-------------------------------|------------------------------------------------------------|-------------------------------------------------------------|
| `CharField` / `TextField` | `'text'`                     | `('text', {'max_nb_chars': 120})`                          | `max_nb_chars` – max length of the string                   |
|                         | `'sentence'`, `'paragraph'`    | `('sentence', {'nb_words': 6})`                            | `nb_words`, `variable_nb_words`                             |
|                         | `'name'`, `'job'`, `'company'` | `('name',)`                                                | None                                                        |
| `IntegerField`          | `'random_int'`                | `('random_int', {'min': 10, 'max': 100})`                  | `min`, `max`                                                |
|                         | `'pyint'`                     | `('pyint', {'min_value': 1, 'max_value': 100})`            | `min_value`, `max_value`, `step`                            |
| `PositiveIntegerField`  | Same as `IntegerField`        | `('random_int', {'min': 0, 'max': 500})`                   | Same as above                                               |
| `DecimalField`          | `'pydecimal'`                 | `('pydecimal', {'left_digits': 4, 'right_digits': 2})`     | `left_digits`, `right_digits`, `positive`, `min_value`, `max_value` |
| `DateField`             | `'date_between'`              | `('date_between', {'start_date': '-5d', 'end_date': '+2w'})`| `start_date`, `end_date`                                    |
|                         | `'past_date'`, `'future_date'`| `('past_date', {'start_date': '-30d'})`                    | `start_date`                                                |
| `DateTimeField`         | `'date_time_between'`         | `('date_time_between', {'start_date': '-1y', 'end_date': 'now'})` | `start_date`, `end_date`                              |
| `BooleanField`          | `'pybool'`                    | `('pybool', {'truth_probability': 75})`                    | `truth_probability`                                         |
| `EmailField`            | `'email'`                     | `('email',)`                                               | None                                                        |
| `URLField`              | `'url'`                       | `('url',)`                                                 | None                                                        |
| `SlugField`             | `'slug'`                      | `('slug',)`                                                | None                                                        |
| `UUIDField`             | `'uuid4'`                     | `('uuid4',)`                                               | None                                                        |
| `TimeField`             | `'time'`                      | `('time', {'pattern': '%H:%M'})`                           | `pattern`, `end_datetime`                                   |
| `BinaryField`           | *(handled via `os.urandom`)*  | —                                                          | Not Faker-supported                                         |

---

## 📌 Notes

- If the field has `choices`, a random choice key is used automatically.
- If no faker_method is provided, sensible defaults are used for each field type.
- Context must be passed as a tuple: `('method_name', {kwargs})`
- Use `fake_field_value(model_instance, field_name, faker_method)` to simplify usage