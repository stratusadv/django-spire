# HTML Renderer

> **Purpose:** Convert any publicly accessible URL to a PDF or PNG file by calling an external HTML renderer service, returning the result as an `InMemoryUploadedFile` ready for storage or download.

---

## Why HTML Renderer?

Generating PDFs and screenshots from Django templates without a headless browser requires an external rendering service. **The HTML Renderer system** provides:

- A single `HtmlRendererClient` class that handles authentication and the HTTP round-trip
- `html_to_pdf` — renders a URL to a PDF and returns it as an uploadable file object
- `html_to_png` — renders a URL to a PNG with optional viewport dimensions
- Automatic base URL resolution for local development (Docker) and production

---

## Quick Start

### 1. Add Required Settings

```python
# settings.py
HTML_RENDERER_URL = 'https://your-renderer-service.example.com'
HTML_RENDERER_ACCESS_KEY = 'your-api-key'

# Development only — the port your local server runs on, accessible from Docker
HTML_RENDERER_PORT = 8000
```

### 2. Render a Page to PDF

```python
from django_spire.contrib.html_renderer.client import HtmlRendererClient

client = HtmlRendererClient()

site_url = HtmlRendererClient.get_site_url()

pdf_file = client.html_to_pdf(
    media_url=f'{site_url}/invoices/42/pdf/',
    file_name='invoice_42.pdf',
)
```

`pdf_file` is an `InMemoryUploadedFile`. Save it to a model `FileField` or return it directly in an `HttpResponse`.

---

## Core Concepts

### `HtmlRendererClient`

The client that communicates with the external rendering service. Reads credentials from Django settings by default, or accepts them as constructor arguments.

```python
from django_spire.contrib.html_renderer.client import HtmlRendererClient
```

**Constructor:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `base_url` | `str \| None` | `settings.HTML_RENDERER_URL` | Base URL of the rendering service |
| `api_key` | `str \| None` | `settings.HTML_RENDERER_ACCESS_KEY` | API key sent as the `x-api-key` header |

**Methods:**

| Method | Description |
|---|---|
| `html_to_pdf(media_url, file_name)` | POST the URL to the `html_to_pdf` endpoint. Returns an `InMemoryUploadedFile` with `content_type='application/pdf'`. |
| `html_to_png(media_url, file_name, screen_width=-1, screen_height=-1)` | POST the URL to the `html_to_png` endpoint with optional viewport dimensions. Returns an `InMemoryUploadedFile` with `content_type='image/png'`. |
| `get_site_url()` *(static)* | Returns `http://host.docker.internal:<HTML_RENDERER_PORT>` in DEBUG mode, or `https://<current Site domain>` in production. |

**Required settings:**

| Setting | Description |
|---|---|
| `HTML_RENDERER_URL` | Base URL of the external rendering service (no trailing slash) |
| `HTML_RENDERER_ACCESS_KEY` | API key for the rendering service |
| `HTML_RENDERER_PORT` | Local dev server port, used when `DEBUG=True` so Docker can reach the host |

---

## Main Operations

### Generating a PDF from a View URL

```python
from django_spire.contrib.html_renderer.client import HtmlRendererClient

client = HtmlRendererClient()
site_url = HtmlRendererClient.get_site_url()

pdf_file = client.html_to_pdf(
    media_url=f'{site_url}/orders/{order.pk}/print/',
    file_name=f'order_{order.pk}.pdf',
)

# Attach to a model field
order.pdf_document = pdf_file
order.save()
```

### Returning a PDF as a Download

```python
from django.http import HttpResponse
from django_spire.contrib.html_renderer.client import HtmlRendererClient

def order_pdf_download_view(request, pk):
    order = Order.objects.get(pk=pk)

    client = HtmlRendererClient()
    site_url = HtmlRendererClient.get_site_url()

    pdf_file = client.html_to_pdf(
        media_url=f'{site_url}/orders/{pk}/print/',
        file_name=f'order_{pk}.pdf',
    )

    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{pk}.pdf"'

    return response
```

### Generating a PNG Screenshot

```python
from django_spire.contrib.html_renderer.client import HtmlRendererClient

client = HtmlRendererClient()
site_url = HtmlRendererClient.get_site_url()

thumbnail = client.html_to_png(
    media_url=f'{site_url}/reports/{report.pk}/preview/',
    file_name=f'report_{report.pk}_thumbnail.png',
    screen_width=1280,
    screen_height=800,
)

report.thumbnail = thumbnail
report.save()
```

Pass `screen_width` and `screen_height` to control the viewport the renderer uses. Omit them (or pass `-1`) to use the renderer service's defaults.

### Using a Custom Renderer Endpoint

```python
client = HtmlRendererClient(
    base_url='https://staging-renderer.example.com',
    api_key='staging-api-key',
)
```

Constructor arguments take precedence over settings, which is useful for testing against a staging renderer without changing `settings.py`.
