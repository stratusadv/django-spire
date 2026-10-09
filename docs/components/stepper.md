# Stepper

## Definition

A stepper shows a numbered sequence of steps in a linear process, and which of them are done, current and upcoming. Use it for a process the user moves through in order, where tabs would wrongly suggest the sections can be visited in any order.

The stepper is a set of CSS classes, not a template. The page writes the list, so a step can hold any markup and can be rendered by Django or by Alpine.

- Shows done, current and upcoming steps.
- Lays out horizontally or vertically.
- Display only: make a step a link or a button by putting one inside it.

## Classes

| Class | Goes on | Effect |
|---|---|---|
| `stepper` | The `<ol>` | Lays the steps out in a row that wraps. |
| `stepper-vertical` | The `<ol>` | Stacks the steps in a column. |
| `stepper-connected` | The `<ol>` | Draws a line from each step to the next. A row no longer wraps. |
| `stepper-step` | Each `<li>` | One step: its mark, then its label. An upcoming step needs no other class. |
| `is-done` | A `stepper-step` | The step is finished. |
| `is-current` | A `stepper-step` | The step is the one in progress. |
| `stepper-mark` | A `<span>` in the step | The circle that holds the step number or an icon. |

The colours come from the theme (`--bs-success`, `--primary`, `--bs-border-color`, `--bs-secondary-color`), so the stepper follows the light and dark themes.

## Example

```html

--8<-- "docs/components/templates/stepper.html"

```
