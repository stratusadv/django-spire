# SCSS Customization

Django Spire ships with its SCSS source files, allowing you to customize colors, typography, and Bootstrap variables to match your project's design.

## How It Works

The SCSS source is bundled inside `django_spire/core/static/django_spire/scss/` and is included automatically when you install the package. This directory contains:

- `bootstrap/` -- Bootstrap 5 SCSS source (bundled, no separate install needed)
- `_theme.scss` -- The default theme entry point with all CSS variables
- `_app.scss` -- Spire component styles
- `_font.scss` -- Poppins font family and web font declarations
- `_*.scss` -- Variables, utilities, components, navigation, and more

## Compiling CSS

Django Spire includes a `compile_scss` management command that uses libsass to compile the bundled SCSS to CSS. No Node.js, npm, or bun required.

```bash
python manage.py compile_scss
```

By default, output goes to `STATIC_ROOT/css/default.css`. You can specify a different output directory:

```bash
python manage.py compile_scss --output my/static/css
```

## Customizing the Theme

To customize colors and variables, create a custom entry point file that extends the theme.

### 1. Create a custom file

In your project's SCSS directory, create a file (e.g., `my_theme.scss`):

```scss
// 1. Define your custom variables BEFORE importing the theme
$primary: #e74c3c;
$primary-light: #ff6b6b;
$secondary: #2c3e50;
$secondary-light: #34495e;
$body-bg: #f8f9fa;
$body-color: #212529;

// Navigation colors
$side-navigation-bg: #2c3e50;
$top-navigation-bg: #ffffff;
$footer-bg: #2c3e50;

// 2. Import the theme entry point
// This will use your variables above and include Bootstrap + Spire styles
@use 'path/to/django_spire/core/static/django_spire/scss/theme' as *;
```

### 2. Compile your custom theme

Since `compile_scss` uses the bundled entry point, compile your custom file separately:

```bash
sass my_theme.scss my_theme.css
```

Or use `libsass` directly:

```python
import sass
css = sass.compile(filename='my_theme.scss', include_paths=['path/to/django_spire/core/static/django_spire/scss'])
```

### 3. Register your custom CSS

Point Django Spire's theme system at your custom CSS file by setting the stylesheet path in your Django settings or model configuration.

## Overriding Bootstrap Variables

You can override any Bootstrap variable before importing the theme. All Bootstrap 5.3 SCSS variables are available:

```scss
// Border radius
$border-radius: 0.5rem;
$border-radius-sm: 0.25rem;
$border-radius-lg: 1rem;

// Typography
$font-family-base: 'Inter', sans-serif;
$font-size-base: 1rem;
$line-height-base: 1.6;

// Spacing
$spacer: 1.5rem;

// Colors (before importing theme)
$primary: #your-color;

@use 'django_spire/core/static/django_spire/scss/theme' as *;
```

## Available Theme Variables

The default theme defines the following customizable variables:

### Semantic Colors

| Variable | Default | Description |
|----------|--------|-------------|
| `$primary` | `#0097c9` | Primary brand color |
| `$primary-light` | `#00b8e6` | Primary light variant |
| `$secondary` | `#797c7d` | Secondary color |
| `$secondary-light` | `#949799` | Secondary light variant |
| `$success` | `#059669` | Success state color |
| `$warning` | `#d97706` | Warning state color |
| `$danger` | `#dc2626` | Danger/error state color |

### Body Colors

| Variable | Default | Description |
|----------|--------|-------------|
| `$body-bg` | `#ffffff` | Light mode background |
| `$body-color` | `#181818` | Light mode text |
| `$body-bg-dark` | `#181818` | Dark mode background |
| `$body-color-dark` | `#ffffff` | Dark mode text |

### Navigation Colors

| Variable | Default | Description |
|----------|--------|-------------|
| `$side-navigation-bg` | `#181818` | Side navigation background |
| `$side-navigation-text-color` | `#ffffff` | Side nav text |
| `$side-navigation-link-color` | `#0097c9` | Side nav links |
| `$side-navigation-link-hover-color` | `#007ba3` | Side nav link hover |
| `$side-navigation-bg-dark` | `#212529` | Side nav dark mode bg |
| `$top-navigation-bg` | `#ffffff` | Top navigation background |
| `$top-navigation-text-color` | `#181818` | Top nav text |
| `$top-navigation-link-color` | `#0097c9` | Top nav links |
| `$top-navigation-link-hover-color` | `#007ba3` | Top nav link hover |
| `$top-navigation-bg-dark` | `#212529` | Top nav dark mode bg |

### Footer Colors

| Variable | Default | Description |
|----------|--------|-------------|
| `$footer-bg` | `#f5f5f6` | Footer background |
| `$footer-text-color` | `#181818` | Footer text |
| `$footer-link-color` | `#0097c9` | Footer links |
| `$footer-link-hover-color` | `#007ba3` | Footer link hover |
| `$footer-bg-dark` | `#212529` | Footer dark mode bg |

### Border Colors

| Variable | Default | Description |
|----------|--------|-------------|
| `$border-color` | `#ededee` | Light mode borders |
| `$border-color-dark` | `#3a3d3e` | Dark mode borders |

## Using as a Reference

Even if you don't use Django Spire's compiled CSS, you can reference the SCSS source to understand how Spire's styles are structured. Copy the `scss/` directory from the installed package to use as a starting point for your own theme.

## Requirements

- Python 3.11+
- `libsass` (included as a dependency of django-spire)
- No Node.js or npm required for compilation