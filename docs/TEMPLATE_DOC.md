# Documentation Writing Guide

This guide defines how documentation is written for this project. Follow it exactly whether you are a human contributor or an AI assistant. All new and updated docs must match this standard.

The canonical reference for what good documentation looks like is the notification app docs:
- `docs/app_guides/notification/app_notifications.md`
- `docs/app_guides/notification/automations.md`
- `docs/app_guides/notification/exceptions.md`

---

## Before You Write

### For AI Assistants

Before writing any documentation, read the following source files for the feature being documented:

- `models.py` — fields, relationships, methods
- `choices.py` or `enums.py` — all choice values and display names
- `querysets.py` — custom queryset methods
- `services/` or `service.py` — service layer methods
- `processor.py` or `processors/` — processing logic
- `exceptions.py` — custom exceptions
- `mixins.py` — any model or view mixins
- `views.py` or `views/` — available views and their URL names
- `urls.py` or `urls/` — URL patterns and names
- `automations.py` — automation entry points
- `managers.py` — manager methods
- `forms.py` — form fields and exclusions

Read the existing doc file too, if one exists, to understand what already exists and what needs changing.

### For Human Contributors

Before writing, gather:
- What problem does this feature solve?
- What are the models/classes involved and what are their fields?
- What is the minimum a developer needs to do to use this feature?
- Are there any external dependencies (third-party services, credentials)?
- What can go wrong (exceptions)?

---

## How to Split Documentation Into Files

Each feature area gets its own subdirectory under `docs/app_guides/<feature>/`. Use the following rules to decide how many files to create:

| Content | File |
|---|---|
| Core model, mixin, quick start, main operations | `<feature>.md` (main guide) |
| Background processing entry points and scheduling | `automations.md` |
| Processing pipeline and dispatch logic | `processors.md` |
| All exceptions for the feature | `exceptions.md` |
| A distinct sub-feature with its own concepts | `<sub_feature>.md` |

**Do not** put exceptions into a main feature doc. They always go in a dedicated `exceptions.md`.

**Do not** create a file for something that is only 3–4 sentences. Fold it into the nearest related doc instead.

---

## File Structure

Every documentation file follows this section order. Omit sections that genuinely do not apply — do not add placeholder sections.

```
# Title

> **Purpose:** One sentence. What this system does and why it exists.

---

## Why <Title>?

Short paragraph intro, then a bullet list of what the system provides.
Bold the system name in the intro sentence.

---

## Quick Start

Numbered steps. Get the developer from zero to working as fast as possible.
Include only what is strictly required to see the feature work.

---

## Core Concepts

One ### subsection per major class or concept.
Each subsection: one-paragraph explanation, import statement, fields/methods table if applicable.

---

## Main Operations

One ### subsection per meaningful thing a developer will do with this feature.
Each subsection has a code example and a short explanation.

---
```

If the feature has external credential requirements (e.g. Twilio, SendGrid), add a **credentials or configuration** step inside Quick Start before the code examples.

---

## Section Writing Rules

### Purpose Blockquote

- One sentence only
- Format: `> **Purpose:** ...`
- Do not end with "etc." — be specific

**Good:**
```
> **Purpose:** Send SMS messages to users via Twilio's REST API, with background processing through automations, batched delivery to respect rate limits, and support for media attachments.
```

**Bad:**
```
> **Purpose:** This guide explains how to use SMS notifications.
```

---

### Why Section

- Open with one sentence: `<Context sentence>. **The <Name> system** provides:`
- Follow with a bullet list of 4–7 concrete capabilities
- Do not use vague bullets like "easy to use" or "flexible"

**Good:**
```
- Background processing through automations to reduce server load
- Priority levels to control display order
```

**Bad:**
```
- Easy to set up
- Flexible and powerful
```

---

### Quick Start

- Use numbered `###` steps
- Each step is the minimum action needed — no explanations of internals here
- The last step should always result in something working or visible
- If the feature requires `INSTALLED_APPS`, that is always Step 1
- If the feature requires migrations, that is always Step 2

---

### Core Concepts

- One `###` per class, model, or concept
- Include the import path as a code block immediately after the heading
- Use a **table** to document fields or methods — do not prose-describe every field
- Tables use this format (no extra column alignment spacing):

```markdown
| Field | Description |
|---|---|
| `name` | Description of the field |
```

---

### Main Operations

- One `###` per operation (creating, querying, updating, filtering, etc.)
- Every operation must have a code example
- Explain *what* the code does after the block, not before
- Operations should be ordered from most common to least common

---

## Style Rules

### Headings

- `#` — document title only
- `##` — top-level sections (Why, Quick Start, Core Concepts, Main Operations)
- `###` — subsections within a section (individual concepts, individual operations)
- **No emojis** in any heading
- **No bold** in headings — the heading itself provides emphasis

### Separators

Use `---` between every `##` section. Do not use `---` between `###` subsections.

### Code Blocks

- Always specify the language: ` ```python `, ` ```javascript `, ` ```bash `, ` ```json `, ` ```html `
- Use real, plausible examples — not `foo`, `bar`, `test_value`
- Examples should use a consistent fictional domain throughout a file (e.g. an order management app, a treasure map app)
- Imports must be accurate — copy them from the actual source files

### Django Template Tags

**Never** write `{% ... %}` or `{{ ... }}` literally in documentation prose or inside non-HTML fenced code blocks. MkDocs will attempt to process them as template directives.

In prose and in non-HTML code blocks, use `{ ... }` instead:

```
# Wrong — will break template rendering in MkDocs
{% include 'django_spire/...' %}

# Correct in prose or non-html code blocks
{ include 'django_spire/...' }
```

### HTML Code Examples

**All `html` code blocks must be extracted into a separate `.html` template file and included via `--8<--`.** Do not write HTML inline in the markdown document.

This is the same pattern used by the components section, and it has two benefits:
1. The template file can contain real `{% %}` and `{{ }}` syntax — the exact, working code is shown
2. The doc stays clean and the HTML is maintainable in one place

**Steps:**

1. Create a `templates/` subdirectory alongside the doc file:
```
docs/app_guides/<feature>/templates/<descriptive_name>.html
```

2. Write the HTML in that file using real Django template syntax:
```html
{% load pagination_tags %}
{% for item in page.object_list %}
    {% include 'myapp/item/item.html' %}
{% endfor %}
```

3. Reference it in the doc with `--8<--` inside the fenced html block:
````
```html
--8<-- "docs/app_guides/<feature>/templates/<descriptive_name>.html"
```
````

**Naming convention for template files:**

Use a descriptive snake_case name that reflects the purpose of the snippet, not the doc section it appears in:

| Good | Bad |
|---|---|
| `pagination_controls.html` | `step_2.html` |
| `comment_list_card.html` | `example.html` |
| `pwa_ios_override.html` | `html_block_1.html` |

### Links Between Docs

Reference related docs with a relative markdown link:

```markdown
See the [Automations](automations.md) guide for setup details.
See the [Notification Exceptions](../notification/exceptions.md) guide.
```

---

## What to Exclude

These sections appear in some older docs but should **not** be written in new or updated docs:

| Excluded Section | Reason |
|---|---|
| API Reference | Method signatures belong in Core Concepts tables, not a separate section |
| Practical Examples | Main Operations covers real usage — a separate examples section is redundant |
| Overview (as a heading) | The Purpose blockquote replaces this |
| Validation (in a feature doc) | Validation rules belong in `exceptions.md` |

---

## Exceptions Documentation (`exceptions.md`)

Every feature that defines custom exceptions gets its own `exceptions.md`. Structure:

1. **Purpose blockquote**
2. **Exception Hierarchy** — ASCII tree of the full inheritance chain
3. One `###` per exception class — import path, description, example output
4. **Status Mapping table** (if the feature has a status lifecycle) — maps each exception to the resulting status and whether it is retried

**Hierarchy tree format:**
```
Exception
└── BaseError
    ├── SpecificErrorA
    └── SpecificErrorB
```

---

## Automations Documentation (`automations.md`)

Structure:
1. Purpose blockquote + Why section
2. Quick Start — the minimal automation registration code
3. Core Concepts — the entry point function and any manager/coordinator classes
4. Main Operations — process ready, process errored, process by type, any cleanup jobs
5. **Scheduling Recommendations table** — what interval to use and why

---

## Processors Documentation (`processors.md`)

Structure:
1. Purpose blockquote + Why section
2. Core Concepts — base class, top-level dispatcher, each channel/type processor
3. Main Operations — single, bulk, ready, errored, and the recommended entry point
4. **Status Lifecycle** — show the `pending → processing → sent` flow

---

## Registering Docs in the Nav

After writing docs, update `mkdocs.yml`. Rules:

- Feature app guides go under `App Guides` in the nav
- Contrib utilities go under `Contrib`
- Core utilities go under `Core`
- Within a feature group, order is: main feature doc(s) first, then `Automations`, `Processors`, `Exceptions` last
- Alphabetical order within a section when no natural dependency order exists

**Example:**
```yaml
- Notification:
    - App Notifications: app_guides/notification/app_notifications.md
    - Email Notifications: app_guides/notification/email_notifications.md
    - SMS Notifications: app_guides/notification/sms_notifications.md
    - Automations: app_guides/notification/automations.md
    - Processors: app_guides/notification/processors.md
    - Exceptions: app_guides/notification/exceptions.md
```

---

## Quick Checklist

Before finishing any documentation, verify:

- [ ] Purpose blockquote is one sentence and specific
- [ ] Why section has a bold system name and a bullet list
- [ ] All imports in code examples are accurate (copied from source)
- [ ] Fields/methods are documented in tables, not prose lists
- [ ] No `{% ... %}` or `{{ ... }}` template tags in prose or non-HTML code blocks — use `{ ... }` instead
- [ ] All `html` code blocks use `--8<-- "docs/..."` to include an external template file
- [ ] External template files are in a `templates/` subdirectory alongside the doc and use real `{% %}` / `{{ }}` syntax
- [ ] No emoji in headings
- [ ] No API Reference section
- [ ] No Practical Examples section
- [ ] Exceptions are in their own file, not in the feature doc
- [ ] `---` separators between all `##` sections
- [ ] New file is registered in `mkdocs.yml` under the correct nav section
