# Agent

## Guidelines
- Always look for relevant skills to load before starting work
- Always use `just` for running any command (it loads the environment properly). Run `just` to see available commands
- Do not comment your code - write it so it doesn't need comments

## Development Commands

Run `just` to see all available commands. Key commands:

```bash
# Server
just run-server

# Database
just migrate
just make-migrations

# Testing
just test                  # Run all tests
just test-app <app>        # Run tests for specific app (e.g., celery)
just test-coverage         # Run tests with coverage
just test-coverage-app <app>  # Run app tests with coverage
just test-failed           # Run only previously failed tests

# Background services
just celery                # Run Celery worker

# Documentation
just docs                  # Run documentation server
just docs-tests            # Build docs with strict mode

# Other
just seed                  # Seed test data
just python <args>         # Run Python with arguments
just opencode              # Run OpenCode with venv activated
just venv                  # Create virtual environment with uv
just venv-upgrade          # Upgrade all packages in venv
```

## Project Overview

Django Spire is a modular Django framework with plugin-based architecture for scalable application development. It provides reusable apps with standardized patterns for Django projects.

### Key Features
- Modular Django apps with standardized AppConfig pattern
- API v1 integration with django-ninja for REST APIs
- Authentication with API key support and permission-based access control
- Intelligent seeding (static, LLM, custom, callable field seeders)
- Theme management (10+ themes, light/dark modes)
- History tracking for model changes
- Activity tracking mixin for user actions
- Generic file and comment systems with content-type relationships
- Help desk ticketing system
- Reporting framework with flexible column types
- Notification system (email, SMS, app, push)
- Service layer pattern for business logic separation

## Framework Structure

```
django_spire/
├── api/                    # REST API integration (django-ninja)
├── ai/                     # AI/LLM integration (chat, context, sms)
├── auth/                   # Authentication (user, group, mfa, permissions)
├── celery/                 # Celery task tracking system
├── comment/                # Comment system with generic content types
├── contrib/                # Shared utilities
│   ├── admin/              # SpireModelAdmin base class
│   ├── breadcrumb/         # Breadcrumb navigation
│   ├── form/               # Form utilities
│   ├── generic_views/      # Portal views (detail, list, form, delete)
│   ├── pagination/         # Pagination utilities
│   └── seeding/            # Intelligent field seeders
├── core/                   # Core functionality (tag, middleware, management)
├── file/                   # File management with generic content types
├── help_desk/              # Help desk/ticketing system
├── history/                # History tracking and activity
├── knowledge/              # Knowledge base management
├── metric/                 # Metrics and reporting framework
├── notification/           # Notification system
├── theme/                  # Theme management
└── changelog/              # Version changelog
```

## Technology Stack
- Python + Django 5.1+
- django-ninja for REST APIs
- Bootstrap 5 for frontend
- PostgreSQL database
- Celery for task queuing
- SendGrid for email, Twilio for SMS

## App Configuration Pattern

Each app follows a standardized pattern in `apps.py`:

```python
class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_app_name'
    name = 'django_spire.app_name'

    MODEL_PERMISSIONS = ({...})    # Optional admin permissions
    REQUIRED_APPS = ('django_spire_core',)
    URLPATTERNS_INCLUDE = 'django_spire.app_name.urls'
    URLPATTERNS_NAMESPACE = 'app_name'
    API_V1_ROUTER = 'django_spire.app_name.api_v1.router'  # Optional
    API_V1_ROUTER_PREFIX = 'app_name'

    def ready(self) -> None:
        check_required_apps(self.label)
```

## Test Project

`test_project/` is a Django project for testing and demonstrating framework capabilities.

### Example Apps
- ai/, celery/, comment/, core/, file/, help_desk/, history/
- home/, infinite_scrolling/, knowledge/, landing/, lazy_tabs/
- model_and_service/, notification/, ordering/, queryset_filtering/
- rest/, sync/, tabular/, wizard/

### Settings
- `base_settings.py` - Base configuration
- `postgres_settings.py` - PostgreSQL configuration
- `sqlite_settings.py` - SQLite for development/testing
- `test_settings.py` - Test configuration

### Seeding
```bash
just seed  # Populate test data (superuser, users, API keys, tickets, etc.)
```

## Development Workflow

1. **Setup**
   ```bash
   just venv              # Create virtual environment
   just make-migrations  # Create migrations
   just migrate           # Run migrations
   just seed              # Seed test data
   ```

2. **Development**
   ```bash
   just run-server        # Start development server
   just celery            # Run Celery worker (separate terminal)
   ```

3. **Testing**
   ```bash
   just test              # Run all tests
   just test-app celery   # Run specific app tests
   just test-coverage     # Run with coverage
   ```

## Best Practices

1. **Service Layer**: Keep business logic in service classes, not models. Use `BaseDjangoModelService` from `contrib.service`
2. **Model Mixins**: Use `HistoryModelMixin` for automatic history tracking
3. **QuerySet Methods**: Define custom QuerySet methods for reusable filters
4. **Intelligence Layer**: Implement AI-driven features through app-specific intelligence sub-apps
5. **Auth Sub-apps**: Separate access control into dedicated auth sub-apps
6. **Breadcrumb Integration**: Use breadcrumb utilities for consistent navigation

## Related Documentation
- [Django Spire Docs](https://django-spire.stratusadv.com)
- [Django Glue](https://django-glue.stratusadv.com/)
- [Dandy](https://dandy.stratusadv.com/)
- [Changelog](docs/changelog/changelog.md)
- [Roadmap](docs/roadmap/2025_roadmap.md)