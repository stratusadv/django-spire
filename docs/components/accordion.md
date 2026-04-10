# Accordion

> **Purpose:** Collapse and expand content sections on click, with two variants — a lightweight local-state accordion and a lazy-loading variant that fetches content from a view the first time it opens.

---

## Why Accordions?

Long detail pages benefit from hiding secondary content behind a click. **The Accordion system** provides:

- A base `accordion.html` with Alpine.js-driven show/hide and a smooth CSS transition
- An `accordion_child_toggle` block for cases where a button inside the header area drives the toggle, not the whole header row
- A `view_glue_accordion.html` that lazily fetches HTML from a server URL on first open, then toggles locally on subsequent clicks
- A shared `show_accordion` state variable available in all blocks so child templates can bind icons, classes, and text to open/closed state

---

## Quick Start

### 1. Extend the Base Accordion

Create a template that extends `accordion.html` and fills the two required blocks:

```html
--8<-- "docs/components/templates/accordion/accordion_basic_usage.html"
```

### 2. Include It in a Page

```html
{ include 'myapp/order/element/order_detail_accordion.html' with obj=order %}
```

Clicking the toggle area expands and collapses the content with a smooth transition.

---

## Core Concepts

### `accordion.html`

The base accordion. Manages a single boolean `show_accordion` state with Alpine.js. The toggle area wraps a `@click="toggle()"` handler, and the content area uses `x-show` and `x-transition`.

**Template path:**
```
django_spire/accordion/accordion.html
```

| Block | Required | Description |
|---|---|---|
| `accordion_toggle` | Yes | The always-visible header. The entire block is wrapped in a `@click="toggle()"` listener. |
| `accordion_child_toggle` | No | Use when a specific child element (e.g. a button) should call `toggle()` rather than the whole header row. |
| `accordion_content` | Yes | The content revealed when the accordion is open. Hidden by default via `x-cloak`. |

The `show_accordion` variable is available in all blocks — use it in `:class` bindings to rotate icons or change styles based on open state.

### `view_glue_accordion.html`

A lazy-loading variant. On first click it calls `render()`, which instantiates a `ViewGlue` object pointed at the URL in `view_url`, fetches the HTML from the server, and injects it into the content div. On subsequent clicks it simply toggles visibility without re-fetching.

**Template path:**
```
django_spire/accordion/view_glue_accordion.html
```

| Block | Required | Description |
|---|---|---|
| `view_url` | Yes | A single-line URL. Used to construct the `ViewGlue` request on first open. |
| `accordion_toggle` | Yes | The clickable header. Must call `render_or_toggle_show()` — it handles both the initial render and subsequent toggles. |
| `accordion_content_class` | No | Extra CSS classes applied to the injected content container div. |

**Alpine.js state available in blocks:**

| Variable | Type | Description |
|---|---|---|
| `show` | `bool` | Whether the content area is currently visible |
| `is_rendered` | `bool` | Whether content has been fetched from the server at least once |

---

## Examples

### Basic Accordion

A single accordion section with a header and collapsible body. Click the header to toggle.


```html
--8<-- "docs/components/templates/accordion/accordion_basic_usage.html"
```

---

### Multiple Independent Accordions

Each accordion manages its own state — opening one does not affect the others.


```html
--8<-- "docs/components/templates/accordion/accordion_multiple_usage.html"
```

---

### Child Toggle

Use `accordion_child_toggle` when a specific element inside the accordion header — rather than the entire row — should control the toggle. The parent header area has no `@click` binding; the child calls `toggle()` directly.


```html
--8<-- "docs/components/templates/accordion/accordion_child_toggle_usage.html"
```

---

### View Glue Accordion

The view glue accordion fetches its content from a Django view the first time it opens. Subsequent clicks toggle the already-loaded content without hitting the server again. The preview below simulates the async load with a short delay.


```html
--8<-- "docs/components/templates/accordion/view_glue_accordion_usage.html"
```

The `view_url` block must resolve to a single-line URL. The view it points to should return a rendered HTML fragment — not a full page — since `ViewGlue` injects the response directly into the content div.
