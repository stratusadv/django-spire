# 🌱 Welcome to Your Django Seeding Toolkit!

### 🚀 Purpose: Make seeding fast, simple, and full of context!

Whether you're testing, demoing, or onboarding new developers — filling your database with realistic data shouldn't be a chore. This module is designed to help you **seed Django models quickly** using a smart combo of techniques:

---

## 🧠 How It Works

We combine different **data generators** to give you flexible and meaningful seed data:

| Type     | What It Does                                           |
|----------|--------------------------------------------------------|
| 🧪 `faker`     | Generates realistic fake data (names, dates, etc.)   |
| 🤖 `llm`       | Uses large language models to generate rich text    |
| 🧊 `static`    | Uses a fixed value for consistent results            |
| 🔁 `callable`  | Runs a function to generate custom dynamic values   |

---

## ⚡ Fast Rebuilds with Caching

We store seed results in a local SQLite cache table — so if you’ve seeded once, you can rebuild your database instantly the next time. Perfect for:

- Rapid development
- Restoring known states
- Testing edge cases

---

## ✨ Why You'll Love It

- 🧠 **Context-aware** data for better realism
- ⏱️ **Cached results** = faster rebuilds
- 🧩 **Modular generators** let you mix faker, LLMs, and functions
---

## 📦 Example

```python
class Recipe(HistoryModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    course = models.CharField(
        max_length=3,
        choices=RecipeCourseChoices.choices,
        default=RecipeCourseChoices.MAIN
    )

    prep_time = models.IntegerField(default=15)
    cook_time = models.IntegerField(default=30)

    servings = models.IntegerField(default=1)
```

```python
recipe_seed = ModelSeeding(
    model_class=Recipe,
    fields = {
        'name': 'llm',
        'description': 'llm' ,
        'course': ('llm', 'Choose a course that matches the name of the recipe.'),
        'prep_time': ('faker', 'random_int', {'min': 5, 'max': 30}),
        'cook_time': ('faker', 'random_int', {'min': 30, 'max': 120}),
        'servings': 'faker',
    },
    exclude_fields=['id'],
)
recipe_seed.generate_model_objects(count=10)
```

This will:

    - Generate context rich text for name, description and course.
    - Prompt the llm to add extra details to course.
    - User faker to generate random prep, cook times and servings
---

## 📘 Next Steps
- 🧪 [Using Faker and Custom Methods](faker.md)
- 🧠 [Getting Creative with LLM Seeding](llm-seeding.md)
- 🔁 [Rebuilding with the Cache](cache-strategy.md)