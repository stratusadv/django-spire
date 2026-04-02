# Ordering Exceptions

> **Purpose:** Provide typed exceptions that surface validation failures when positions are invalid, giving calling code a clear signal to catch and respond to ordering errors.

---

## Why Typed Exceptions?

Rather than silently clamping positions or returning error codes, the ordering system raises structured exceptions at the point of validation. This allows you to:

- Catch ordering failures separately from unexpected errors
- Inspect individual validation messages to surface meaningful feedback
- Trust that any unraised call succeeded

---

## Exception Hierarchy

```
Exception
└── OrderingMixinGroupError
└── OrderingMixinError
```

Both exceptions are independent — `OrderingMixinGroupError` wraps a list of `OrderingMixinError` instances collected during validation.

---

## Exceptions

### `OrderingMixinError`

Represents a single validation failure. Each failed rule produces one `OrderingMixinError` with a message describing the problem.

```python
from django_spire.contrib.ordering.exceptions import OrderingMixinError
```

### `OrderingMixinGroupError`

Raised by `move_to_position` when one or more validation rules fail. Wraps all collected `OrderingMixinError` instances from that validation pass.

```python
from django_spire.contrib.ordering.exceptions import OrderingMixinGroupError
```

---

## Catching Ordering Errors

```python
from django_spire.contrib.ordering.exceptions import OrderingMixinGroupError

try:
    task.ordering_services.processor.move_to_position(
        destination_objects=Task.objects.all(),
        position=999,
    )
except OrderingMixinGroupError as e:
    for error in e.args[1]:
        print(error)  # OrderingMixinError message
```

---

## Validation Rules

`move_to_position` validates the requested position before any database writes. All failing rules are collected and raised together.

| Rule | Error Message | Condition |
|---|---|---|
| Position is non-negative | `Position must be a positive number.` | `position < 0` |
| Position is an integer | `Position must be a positive number.` | `not isinstance(position, int)` |
| Position within list bounds | `Position must be less than the number of destination objects.` | `position > len(destination_objects)` |
