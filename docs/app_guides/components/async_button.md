# Async Button

> **Purpose:** Run one call to the server from a button that is switched off until the call settles, so a second click sends nothing and the button comes back if the call fails.

---

## Why an Async Button?

A plain button that calls the server stays clickable while it waits. A double click sends the call twice, which for a save or a duplicate means two rows. **The async button** provides:

- One call for any number of clicks while it is running
- A disabled state for the length of the call, and a spinner in the template version
- A reset when the call fails, so the user can try again
- A flag that several buttons can share, so only one of them runs at a time
- One attribute to add the behaviour to any element, with no template

---

## Quick Start

### 1. Include the button

```html
--8<-- "docs/app_guides/components/templates/async_button_include.html"
```

The button calls `component.publish()`. While that runs it is disabled and shows a spinner in place of its icon.

---

## Core Concepts

### `async_button.html`

The button as a template, at `django_spire/button/async_button.html`.

| Argument | Description |
|---|---|
| `x_button_click` | The call to wait for, as an Alpine expression such as `component.save()` |
| `x_busy` | Optional. The name of a flag in an enclosing Alpine scope that several buttons share |
| `button_text` | The label |
| `button_class` | Bootstrap button classes. Defaults to `btn-primary text-light` |
| `button_icon` | Optional icon classes, such as `bi bi-trash` |
| `button_title` | Optional tooltip |

### `asyncButton`

The behaviour itself, registered with Alpine by `django_spire/js/components/async_button.js`. The template is this plus markup.

```javascript
asyncButton(call, busyName)
```

| Argument | Description |
|---|---|
| `call` | A function that returns a promise. The button is off until it settles |
| `busyName` | Optional. The name of a shared flag, as for `x_busy` |

| Name | Description |
|---|---|
| `isRunning` | True while this button's own call is running |
| `isBusy` | True while this button is off: its call is running, or the shared flag is set |

---

## Main Operations

### Adding the Behaviour to Any Element

```html
--8<-- "docs/app_guides/components/templates/async_button_attribute.html"
```

`x-bind="asyncButton(...)"` gives an element the click handling and the disabled state with one attribute. Use it for an icon button, or any button whose markup the template does not fit.

### Running Two Steps

```html
--8<-- "docs/app_guides/components/templates/async_button_two_steps.html"
```

The function must return a promise that settles when the work is done. A single call does that already, so `() => component.save()` is enough. When something has to happen after the call, mark the function `async` and `await` the call, as here. Without that the button would switch back on before the work had finished.

### Sharing a Flag Between Buttons

```html
--8<-- "docs/app_guides/components/templates/async_button_shared_flag.html"
```

Buttons that name the same flag take turns. The one that was clicked sets the flag for the length of its call, and the others are off while it is set. Declare the flag on an element around the buttons.

### Using It on an Element With Its Own Alpine Data

```html
--8<-- "docs/app_guides/components/templates/async_button_own_data.html"
```

The one-attribute form gives the element its Alpine data. An element that must set `x-data` itself uses `asyncButton` as that data and binds its `button`. The result is the same.

---

## Things to Know

- **A failed call is not hidden.** The button switches back on and the failure is passed on. For a Glue call, Spire's `base.html` shows the user an error message.
- **It is not Alpine's `x-bind:disabled` alone.** Disabling a button in the page takes a moment to apply, so two clicks in the same instant can both get through. `asyncButton` also checks before it starts.
- **A project that does not extend Spire's `base.html`** must load the scripts in `django_spire/js/components/` itself.
