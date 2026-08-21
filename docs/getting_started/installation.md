# Installation

> **Purpose:** how to add Django Spire to a Django project — installation, required settings, and the wiring each app expects.

---

## Python & Django

Django Spire requires Python **3.12+** and Django **6.0+**.

---

## Pip

Like most Python packages you can install Django Spire with pip:

```bash
pip install django-spire
```

Or, if you manage the environment with `uv`:

```bash
uv add django-spire
```

All runtime dependencies (Django, `django-glue`, `celery`, `twilio`, `psycopg2`, and more) are installed with the package.

---

## Django Apps

Import each Django Spire module you need independently — do not import `django_spire` as a whole. Only add the modules with green check marks on the [home page](../index.md) to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_spire.core',
    'django_spire.auth',
    'django_spire.auth.user',
    'django_spire.auth.group',
    'django_spire.history',
    'django_spire.history.activity',
    'django_spire.comment',
    'django_spire.file',
    'django_spire.help_desk',
    'django_spire.notification',
    'django_spire.notification.email',
    'django_spire.contrib.options',
    'django_spire.contrib.ordering',
    'django_glue',
]
```

If you use [Celery](https://docs.celeryq.dev/), install `django_spire.celery` and point it at your broker.

---

## Middleware

`ActivityUserMiddleware` must be listed **after** `AuthenticationMiddleware` so activity records are attributed to the request user:

```python
MIDDLEWARE = [
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_spire.history.activity.middleware.ActivityUserMiddleware',
    ...
]
```

Django system checks warn (`django_spire_history_activity.W001`/`W002`) if it is missing or misordered.

---

## Templates

Add the Spire context processor so templates can access navigation defaults and registered auth controllers:

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                ...
                'django_spire.core.context_processors.django_spire',
            ],
        },
    },
]
```

Base your page templates on `django_spire/base/base.html` — it loads the Spire JS globals (`Spire`, `ajax`, `modal`, `Glue`), Alpine.js, Bootstrap, and the compiled Spire SCSS.

---

## URLs

Each Spire app declares `URLPATTERNS_INCLUDE` + `URLPATTERNS_NAMESPACE`, which are auto-discovered by the single Spire URL include:

```python
# urls.py
from django_glue import django_glue_urls
from django_spire.shortcuts import django_spire_urls

urlpatterns = [
    ...
]

urlpatterns += django_glue_urls()
urlpatterns += django_spire_urls()
```

Spire routes are mounted under the `django_spire:` namespace (e.g. `django_spire:auth:admin:login`).

---

## Auth

Point Django's auth URLs at Spire's login/logout views:

```python
LOGIN_URL = 'django_spire:auth:admin:login'
LOGIN_REDIRECT_URL = 'django_spire:auth:redirect:login'
LOGOUT_REDIRECT_URL = 'django_spire:auth:admin:login'
```

Per-app access control is wired through auth controllers registered in `DJANGO_SPIRE_AUTH_CONTROLLERS`:

```python
DJANGO_SPIRE_AUTH_CONTROLLERS = {
    'my_app': 'my_app.auth.controller.MyAppAuthController',
}
```

---

## Optional Features

| Feature | App / Setting | Notes |
|---------|---------------|-------|
| AI chat & SMS | `django_spire.ai`, `django_spire.ai.chat`, `django_spire.ai.sms` | Requires OpenAI API credentials in your environment |
| SMS notifications / auth | `django_spire.notification.sms`, `django_spire.auth.sms` | Requires Twilio credentials (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`) |
| Email notifications | `django_spire.notification.email` | Any Django email backend; SendGrid is used in the reference project |
| Push notifications | `django_spire.notification.push` | Web-push delivery |
| Knowledge base | `django_spire.knowledge` | Search, entry versioning, LLM preprocessing |
| Metric reporting | `django_spire.metric`, `django_spire.metric.domain`, `django_spire.metric.report`, `django_spire.metric.visual` | Reports, dashboards, signage |
| API | `django_spire.api` | django-ninja API mounted at `api/v1/`, keyed via `ApiAccess` |
| File handling | `django_spire.file` | File fields, validators, upload widgets; S3 via `django-storages` |
| Maintenance mode | `django_spire.core` | `MAINTENANCE_MODE` setting + `MaintenanceMiddleware` |

---

## Migrations & Seeding

Run migrations as usual. Test/demo data is generated with the [seeding framework](../app_guides/seeding/overview.md) — the reference project runs a seed script per app:

```bash
python test_project/seed.py
```
