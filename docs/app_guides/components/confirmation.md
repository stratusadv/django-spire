# Confirmation Components

> **Purpose:** Ask the user to confirm one action in a Glue component, perform it on the server when they do, and report the outcome to whatever showed the prompt.

---

## Why Confirmation Components?

An action that cannot be undone should ask first, and the asking is the same every time: a title, a sentence, a Cancel button and a Confirm button. **The confirmation components** provide:

- A prompt worded when it is built, with no template to write
- Confirm and Cancel reported as events, so the prompt does not need to know what it is shown in
- An access level required to confirm, checked on the server
- Buttons that cannot be clicked twice, or clicked while the action is running
- A ready-made confirmation for one row of any model, and two for deleting one
- Cancel that makes no request to the server

---

## Quick Start

A [CRUD scroll](scroll.md) already confirms a delete, with no code. To confirm some other action, write the confirmation, return it from a callable, and show it.

### 1. Write the confirmation

```python
from django_spire.core.components import BaseModelActionConfirmationComponent


class TaskArchiveConfirmationComponent(BaseModelActionConfirmationComponent):
    def perform_action(self) -> None:
        self.instance.services.processor.archive()
```

### 2. Return it from a callable

```python
from django_glue import Glue

from app.task.models import Task


class TaskBoardComponent(Glue.Component):
    template = 'task/component/task_board.html'

    @Glue.attr(required_access=Glue.Access.CHANGE)
    def archive_confirmation(self, pk: int) -> TaskArchiveConfirmationComponent:
        return TaskArchiveConfirmationComponent(
            instance=Task.objects.active().get(pk=pk),
            title='Archive this task?',
            confirm_label='Archive',
            access=self.access,
        )
```

### 3. Show it in a modal

```html
--8<-- "docs/app_guides/components/templates/confirmation_open_in_modal.html"
```

Clicking Archive opens the prompt. Confirming archives the task and fires `confirmed`; Cancel fires `cancelled`. The page closes the modal in both cases.

---

## Core Concepts

### `BaseConfirmationComponent`

Asks the user to confirm one action. A subclass performs the action in `on_confirm()`.

```python
from django_spire.core.components import BaseConfirmationComponent
```

| Member | Description |
|---|---|
| `title` | The prompt's heading. Defaults to "Are you sure?" |
| `message` | A sentence under the heading. None by default |
| `confirm_label` | The text of the confirm button. Defaults to "Confirm" |
| `confirm_access` | The access the user needs in order to confirm. Defaults to `VIEW` |
| `on_confirm()` | Perform the action and return a dict, which becomes the detail of `confirmed` |
| `confirmed` | The event fired after the action is performed |
| `cancelled` | The event raised when the user cancels |

`title`, `message` and `confirm_label` are given when the confirmation is built. They are plain text and are escaped.

The component closes nothing. Whoever shows it listens for the two events and puts it away, so the same confirmation works in a modal or inline on a page.

### `BaseModelActionConfirmationComponent`

A confirmation for one action on one row of a model. It works for any model without a subclass for each.

```python
from django_spire.core.components import BaseModelActionConfirmationComponent
```

| Member | Description |
|---|---|
| `instance` | The row, given when the confirmation is built |
| `model_name` | The model's verbose name, for wording the prompt |
| `perform_action()` | Perform the action on `self.instance`. A subclass writes this |

`confirmed` carries the row's primary key as `pk`.

### `BaseModelDeleteConfirmationComponent`

A model action confirmation worded and guarded as a delete: it shows a delete prompt that names the row, and confirming needs `DELETE` access. A subclass deletes the row in `perform_action()`.

```python
from django_spire.core.components import BaseModelDeleteConfirmationComponent
```

### `ModelSetDeletedConfirmationComponent` and `ModelDeleteConfirmationComponent`

The two ready-made ways to delete a row.

```python
from django_spire.core.components import (
    ModelDeleteConfirmationComponent,
    ModelSetDeletedConfirmationComponent,
)
```

| Component | Confirming |
|---|---|
| `ModelSetDeletedConfirmationComponent` | Soft-deletes the row with `set_deleted()`. The model must use Spire's history mixin |
| `ModelDeleteConfirmationComponent` | Deletes the row from the database with the model's `delete()` |

A CRUD scroll uses the first by default.

---

## Main Operations

### Wording a Prompt

```python
TaskArchiveConfirmationComponent(
    instance=task,
    title='Archive this task?',
    message='It will be hidden from every list.',
    confirm_label='Archive',
)
```

Any of the three left out keeps the template's own wording. A delete confirmation's defaults name the row and its model.

### Adding Markup to a Prompt

```python
class TaskArchiveConfirmationComponent(BaseModelActionConfirmationComponent):
    template = 'task/component/task_archive_confirmation.html'

    def perform_action(self) -> None:
        self.instance.services.processor.archive()
```

```html
--8<-- "docs/app_guides/components/templates/confirmation_archive.html"
```

A template that extends the base can replace the title, the message and the confirm button, for an icon or a different button style. Keep `x_busy='isSettling'` on the confirm button: it is what stops Cancel being clicked while the action runs.

### Deleting a Row in the Application's Own Way

```python
class TaskDeleteConfirmationComponent(BaseModelDeleteConfirmationComponent):
    def perform_action(self) -> None:
        self.instance.services.processor.remove_from_board()
        self.instance.set_inactive()
```

The confirmation keeps the delete wording and the `DELETE` access check, and deletes however the model needs. Give it to a list with `ComponentDeleteOptions(component=TaskDeleteConfirmationComponent)`.

### Requiring More Access to Confirm

```python
from django_glue import Glue


class InvoiceApprovalConfirmationComponent(BaseModelActionConfirmationComponent):
    confirm_access = Glue.Access.CHANGE

    def perform_action(self) -> None:
        self.instance.services.processor.approve()
```

`confirm_access` is checked on the server when the user confirms. Cancel is never restricted.

### Confirming Something That Is Not a Row

```python
class ClearCacheConfirmationComponent(BaseConfirmationComponent):
    def on_confirm(self) -> dict:
        cleared = cache_service.clear()

        return {'cleared': cleared}
```

Subclass the base directly and write `on_confirm()`. The dict it returns reaches the listener as the detail of `confirmed`.

### Scoping the Row a Confirmation Acts On

```python
from django_glue import Glue

from app.task.models import Task


class MyTaskDeleteConfirmationComponent(ModelSetDeletedConfirmationComponent):
    @Glue.ComponentParameter
    def instance(self, pk: int) -> Task:
        return Task.objects.active().get(pk=pk, assigned_to=self.request.user)
```

A confirmation is built with a row, and looks that row up again by its primary key when the user confirms. By default that lookup has no conditions, so a row the user could act on when the prompt opened can still be acted on when they confirm, even if it has since been reassigned. Overriding `instance` repeats the application's rule at that moment: a row outside it is reported as not found, and nothing is done.

The method takes the primary key and its return annotation names the model. Do this for a list whose queryset is how it enforces who may act on a row.

---

## Things to Know

- **Events can be raised by the browser.** `cancelled` is raised in the browser, with Glue's `$dispatch`, and needs django-glue 1.3.0. A listener on the server must not treat any event as proof that an action happened.
- **A confirmation needs `ModelSetDeletedConfirmationComponent`'s model to have `set_deleted()`.** A model without Spire's history mixin fails when the user confirms. Use `ModelDeleteConfirmationComponent`, or a subclass, for those.
