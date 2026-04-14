---
name: python-style
description: Python coding standards and best practices
---

# Python Style Guide

## Philosophy: Managing Complexity

The fundamental goal is to reduce complexity, which manifests as change amplification (simple changes requiring modifications everywhere), cognitive load (information developers must retain), and unknown unknowns (non-obvious what needs changing).

Design decisions should pull complexity downward—handle complexity internally rather than exposing it to callers. This requires a strategic mindset that invests 10-20% of time in simplifying designs, rather than tactical programming that focuses only on getting features working quickly.

### Tactical vs Strategic Programming

Tactical programming accumulates complexity by taking shortcuts. Strategic programming invests in designs that remain simple over time.

```python
# TACTICAL: Global state, hard to test or scale
config_value = "default"

def process_data_tactical(item):
    global config_value
    print(f"Processing {item} with {config_value}")


# STRATEGIC: Encapsulated, testable, flexible
class DataProcessor:
    def __init__(self, config):
        self.config = config

    def process(self, item):
        print(f"Processing {item} with {self.config}")
```

## Core Principles

### Self-Documenting Code

Code must be self-explanatory through clear naming and structure. Comments and docstrings are never used—type hints provide the necessary documentation. If you want to add a comment, rename the variable or break the function into smaller pieces instead.

### Type Hints

Always use type hints for function parameters and return values. Import `from __future__ import annotations` at the top of every file. Use `TYPE_CHECKING` guards for imports to avoid circular dependencies, `TypeVar` for generic patterns, and `ClassVar` for class-level type hints.

### Deep Modules, Simple Interfaces

Modules should be deep—providing powerful functionality through simple interfaces that hide implementation complexity. Shallow modules where the interface is as complex as the implementation add no value and increase cognitive load.

```python
# SHALLOW: Pass-through adds no value (avoid)
class AttributeWrapper:
    def __init__(self):
        self.data = {}

    def add_null_value(self, attribute):
        self.data[attribute] = None


# DEEP: Hides complex logic behind simple interface (prefer)
class TextSearcher:
    def __init__(self, text):
        self.text = text

    def find_all(self, pattern):
        import re
        return [m.start() for m in re.finditer(pattern, self.text)]
```

### Pull Complexity Downward

Module developers should handle complexity internally rather than forcing callers to manage it. Configuration parameters are often excuses to avoid design decisions—compute defaults automatically when possible.

```python
# COMPLEXITY PUSHED UP: Caller handles retries (avoid)
def send_request_manual(data):
    # Caller must implement retry loop and timing
    pass


# COMPLEXITY PULLED DOWN: Internalized logic (prefer)
import time

class ReliableRequester:
    def send(self, data, max_retries=3):
        for i in range(max_retries):
            try:
                return "Success"
            except Exception:
                time.sleep(1)
        raise Exception("Failed after retries")
```

### Information Hiding

Encapsulate design decisions within modules so they don't leak to other modules. Exposing internal data structures creates dependencies that make changes difficult.

```python
# LEAKAGE: Exposes internal representation (avoid)
class HTTPRequestLeak:
    def __init__(self):
        self.params = {"user_id": "123"}

    def get_params(self):
        return self.params  # Caller can modify internal state


# HIDING: Encapsulates representation (prefer)
class HTTPRequestHidden:
    def __init__(self):
        self.__params = {"user_id": "123"}

    def get_parameter(self, name):
        return self.__params.get(name)

    def get_int_parameter(self, name):
        val = self.get_parameter(name)
        return int(val) if val else None
```

### General-Purpose vs Special-Purpose

Design interfaces to be somewhat general-purpose. Special-purpose methods tied to specific use cases create shallow APIs. General mechanisms support more use cases with less code.

```python
# SPECIAL-PURPOSE: Tied to specific UI action (avoid)
class TextEditor:
    def backspace(self, cursor_pos):
        pass  # Only deletes one char to left


# GENERAL-PURPOSE: Flexible mechanism (prefer)
class TextEditor:
    def delete(self, start_pos, end_pos):
        pass  # Supports backspace, delete, range deletion


# Usage: editor.delete(cursor_pos - 1, cursor_pos)
```

## File Structure

### Import Order

Imports must follow a consistent order: `from __future__ import annotations`, `from typing import TYPE_CHECKING`, standard library, third-party, local application imports, then the `TYPE_CHECKING` block at the end.

### String Quotes

**Always use single quotes (`'`) for strings.** Double quotes (`"`) should only be used when the string contains a single quote character.

```python
# CORRECT
name = 'John'
message = 'Hello world'
url = 'https://example.com'

# CORRECT (when string contains single quote)
greeting = "Don't stop"

# INCORRECT
name = "John"
message = "Hello world"
```

### Function Call Formatting

**When a function call has multiple arguments or keyword arguments, place each argument on its own line.** This improves readability and makes it easier to add/remove arguments.

```python
# CORRECT - Multiple arguments on separate lines
catalog = Catalog.objects.create(
    user=self.super_user,
    company=self.company,
    field_1='Catalog One'
)

url = company_reverse(
    'company:page:detail',
    self.company,
    pk=self.company.pk
)

result = access_object_list_by_company(
    Catalog,
    self.company,
    field_1='Catalog One'
)

# INCORRECT - Multiple arguments on same line
catalog = Catalog.objects.create(user=self.super_user, company=self.company, field_1='Catalog One')
url = company_reverse('company:page:detail', self.company, pk=self.company.pk)
```

**Single argument function calls can remain on one line:**

```python
# CORRECT
result = get_object_or_404(Catalog, id=catalog.id)
assert result is True
```

### Dictionary and List Formatting

**When creating dictionaries or lists with multiple items, place each item on its own line.**

```python
# CORRECT
data = {
    'key1': 'value1',
    'key2': 'value2',
    'key3': 'value3'
}

items = [
    'item1',
    'item2',
    'item3'
]

# CORRECT - Single item dictionaries/lists can be inline
data = {'key': 'value'}
items = ['single']

# INCORRECT
data = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
items = ['item1', 'item2', 'item3']
```

## Naming Conventions

- **Classes**: PascalCase (e.g., `UserProfileService`, `InventoryQuerySet`)
- **Functions/Methods**: snake_case (e.g., `get_or_create_for_user`, `bulk_filter`)
- **Variables**: snake_case (e.g., `company_user`, `inventorys`)
- **Constants**: UPPERCASE (e.g., `DEFAULT_USER_OPTIONS`, `CANADA_TIMEZONES`)
- **Private functions/methods**: underscore prefix (e.g., `_form_view`, `_is_valid_uuid`)

## Code Organization

### Functions and Methods

Keep functions small and focused on a single task. Extract shared logic into private helper functions. Use descriptive names that explain what the function does. Avoid nested logic and flatten when possible. Avoid pass-through methods that do nothing but call another method—each function should add meaningful value. Handle edge cases internally rather than forcing callers to validate inputs.

### Classes

Declare class attributes clearly at the top. Use mixins as parent classes where appropriate. Implement `__str__` methods for models. Hide internal state using private attributes (`__`) for implementation details. Provide general-purpose methods rather than special-purpose actions.

## What to Avoid
- **NEVER** add comments (inline or block)
- **NEVER** add docstrings to functions, methods, or classes
- **NEVER** over-engineer simple solutions
- **NEVER** use verbose naming when concise works
- **NEVER** add explanatory text anywhere
- **NEVER** create shallow modules that add no value
- **NEVER** expose internal data structures or implementation details
- **NEVER** pass through parameters that intermediate layers don't use
- **NEVER** use double quotes for strings (use single quotes instead)
- **NEVER** put multiple function arguments on the same line
- **NEVER** put multiple dictionary/list items on the same line
