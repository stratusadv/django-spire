# Agent

## Guidelines
- Always look for relevant skills to load
- Do not comment your code. You should never write anything complicated enough that needs comments.

## Project Overview

Django Spire is a modular Django framework that makes application development scalable and extensible. The framework follows a plugin-based architecture where functionality is organized into discrete apps that can be easily integrated.

### Key Features
- Modular Django app architecture with standardized AppConfig pattern
- API v1 integration with django-ninja for REST APIs
- Authentication system with API key support and permission-based access control
- Seeding capabilities using intelligent field seeders (static, LLM, custom, callable)
- Theme management with 10+ pre-built themes
- History tracking for model changes (CREATED, UPDATED, DELETED, ACTIVE, INACTIVE)
- Activity tracking mixin for user actions
- Generic file and comment systems with content-type relationships
- Help desk ticketing system with priority and status management
- Reporting framework with flexible column types and formatting
- Notification system for email and app notifications
- Profiling middleware for performance monitoring

### Version
- Current: 0.28.7

## Architecture

### Core Structure

```
django_spire/
├── api/                  # API integration (django-ninja)
├── ai/                   # AI/LLM integration
├── auth/                 # Authentication system (user, group, MFA, permissions)
├── comment/              # Comment system with generic content types
├── contrib/              # Shared utilities and helpers
├── core/                 # Core framework functionality
├── file/                 # File management with generic content types
├── help_desk/            # Help desk/ticketing system
├── history/              # Model history and activity tracking
├── knowledge/            # Knowledge base management (entry, version, collection)
├── metric/               # Metrics and reporting framework
├── notification/         # Email and app notifications
├── profiling/            # User profiling and performance monitoring
├── theme/                # Theme management (10+ themes, light/dark modes)
└── urls.py               # Main URL configuration
```

### App Configuration Pattern

Each app follows a standardized configuration pattern in `apps.py`:

```python
class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_app_name'
    name = 'django_spire.app_name'
    
    # Model permissions for admin (optional)
    MODEL_PERMISSIONS = (
        {
            'name': 'app_name',
            'verbose_name': 'App Name',
            'model_class_path': 'django_spire.app_name.models.ModelName',
            'is_proxy_model': False,
        },
    )
    
    # Required apps that must be installed
    REQUIRED_APPS = ('django_spire_core',)
    
    # URL patterns for admin UI
    URLPATTERNS_INCLUDE = 'django_spire.app_name.urls'
    URLPATTERNS_NAMESPACE = 'app_name'
    
    # Optional API v1 router (for apps with REST endpoints)
    API_V1_ROUTER = 'django_spire.app_name.api_v1.router'
    API_V1_ROUTER_PREFIX = 'app_name'
    
    def ready(self) -> None:
        check_required_apps(self.label)
```

## Core Framework Apps

### django_spire.api
REST API integration using django-ninja with:
- API key authentication with HMAC-SHA256 hashing
- Permission levels: VIEW (1), ADD (2), CHANGE (3), DELETE (4)
- Rate limiting: anon 1/s, authenticated 150/s
- Auto-discovery of app routers
- API key management via admin interface

#### django_spire.help_desk
Help desk ticketing system with:
- Ticket creation, priority, status, and purpose tracking
- Notification service for new ticket creation
- QuerySet with active/deleted filtering
- Service layer for business logic
- Status: READY, IN_PROGRESS, ON_HOLD, RESOLVED, CLOSED
- Priority: LOW, MEDIUM, HIGH, CRITICAL

#### django_spire.metric.report
Reporting framework with:
- BaseReport abstract class for custom reports
- Column types: TEXT, NUMBER, DOLLAR, PERCENT (with decimal variants)
- Report rows with formatting options (bold, page breaks, borders)
- Report registry for hierarchical report organization
- ReportRun model for tracking report executions
- Markdown export capability

#### django_spire.knowledge
Knowledge base system with:
- Entry: Content items with version history
- Version: Different versions of entries with blocks
- Collection: Hierarchical organization of entries
- Generic content relationships

#### django_spire.notification
Notification system with:
- Base Notification model for tracking
- Email notifications with attachments, CC, BCC support
- SMS notifications (Twilio integration)
- App notifications (push-style)
- Automation system for scheduled notifications
- Throttling support

#### django_spire.file
File management with:
- Generic content-type relationships
- File metadata (name, type, size)
- History tracking
- QuerySet with active filtering

#### django_spire.comment
Comment system with:
- Generic content-type relationships
- Parent-child relationships (replies)
- User references
- Edit tracking
- Username @mention scraping
- History tracking

#### django_spire.theme
Theme management with:
- 10+ theme families (Default, Ayu, Catppuccin, Gruvbox, Material, Nord, One Dark Pro, Palenight, Rose Pine, Tokyo Night)
- Light and dark modes
- CSS stylesheet generation
- Theme configuration via settings

#### django_spire.auth
Authentication system with:
- AuthUser (proxy of Django User with activity tracking)
- AuthGroup (proxy of Django Group with activity tracking)
- MFA support (authenticator app, SMS)
- Permission-based access control
- Authentication controllers for UI views

#### django_spire.history
History tracking with:
- HistoryModelMixin for automatic history events
- HistoryEvent choices: CREATED, UPDATED, DELETED, ACTIVE, INACTIVE, UNDELETED
- GenericRelation for querying history events
- ActivityMixin for user action tracking

#### django_spire.profiling
Performance profiling with:
- Profiling middleware for request tracking
- Profiling panel for debug toolbar
- Thread locking for concurrent access

## Technology Stack

- **Backend**: Python, Django 5.1+
- **API Framework**: django-ninja (async-ready, Pydantic-based)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: PostgreSQL
- **Storage**: AWS S3
- **Email**: SendGrid

## Core Components

### django_spire.contrib

Shared utilities and helpers:

- **seeding**: Intelligent field seeders
  - Static, LLM, custom, and callable field types
  - DjangoModelSeeder for automatic model seeding
  - Intelligence bots for automated seeder generation
  - Management command: `python manage.py seeding`

- **service**: BaseDjangoModelService for business logic
  - Separates business logic from models
  - Handles field updates with transaction support
  - File field deferral for proper model saving

- **generic_views**: Portal views for admin UI
  - detail_view, list_view, form_view, delete_form_view
  - Breadcrumb integration
  - Activity tracking

- **admin**: SpireModelAdmin for automatic admin configuration
  - Auto-configures list_display, list_filter, search_fields
  - Read-only fields for created_datetime, is_active, is_deleted

- **breadcrumb**: Breadcrumbs system
  - add_breadcrumb, add_obj_breadcrumb methods
  - Integration with portal views

- **contrib/session**: Session controllers

- **contrib/options**: Options mixins

- **contrib/help**: Help template tags

### django_spire.auth

Authentication system with:

- **AuthUser**: Proxy of Django User with activity tracking
- **AuthGroup**: Proxy of Django Group with activity tracking
- **MFA**: Multi-factor authentication (authenticator app, SMS)
- **Permissions**: Permission-based access control
- **AuthController**: BaseAuthController and AppAuthController
  - Custom permission methods (can_add, can_change, can_delete, can_view)
  - Decorator-based permission checking

### django_spire.history

History tracking system with:

- **HistoryModelMixin**: Automatic history events on save
  - CREATED, UPDATED, DELETED, ACTIVE, INACTIVE, UNDELETED
  - is_active, is_deleted fields
  - history_events GenericRelation

- **ActivityMixin**: User action tracking
  - add_activity method
  - verb, information, target fields

- **HistoryEvent**: Event model for tracking changes
  - content_type, object_id for generic relationships
  - event, created_datetime fields

### django_spire.help_desk

Help desk ticketing system with:

- **HelpDeskTicket**: Ticket model with history tracking
  - Priority: LOW, MEDIUM, HIGH, CRITICAL
  - Status: READY, IN_PROGRESS, ON_HOLD, RESOLVED, CLOSED
  - Purpose: Ticket purpose tracking

- **HelpDeskTicketService**: Business logic service
  - create() method for ticket creation
  - Notification service for new ticket alerts

- **QuerySet**: Custom query methods
  - active(), deleted() filters

### django_spire.metric.report

Reporting framework with:

- **BaseReport**: Abstract base class for custom reports
  - title, description, columns, rows
  - add_column(), add_row(), add_divider_row()
  - to_markdown() export

- **Column types**:
  - TEXT, NUMBER, DOLLAR, PERCENT (with 1-3 decimal variants)
  - Left/right alignment based on type

- **ReportRegistry**: Hierarchical organization
  - add_registry() for nested categories
  - get_report_from_key_stack() for retrieval

- **ReportRun**: Tracking model
  - report_key_stack for hierarchy
  - datetime field for execution time

### django_spire.knowledge

Knowledge base system with:

- **Entry**: Content items with version history
- **Version**: Different versions of entries
- **Block**: Content blocks within versions
- **Collection**: Hierarchical organization

### django_spire.file

File management with:

- **File**: Generic content-type model
  - content_type, object_id, content_object
  - file, name, type, size fields
  - related_field for field association

- **FileQuerySet**: Custom query methods
  - active() filter

- **GenericForeignKey**: Content-type relationships

### django_spire.comment

Comment system with:

- **Comment**: Generic content-type model
  - Parent-child relationships (replies)
  - User references
  - @mention scraping

- **CommentQuerySet**: Custom query methods

- **History tracking**: CREATED, UPDATED events

### django_spire.theme

Theme management with:

- **Theme**: Theme class for configuration
  - 10+ theme families
  - Light and dark modes
  - CSS stylesheet generation
  - from_string() for parsing
  - get_available(), get_default() methods

- **Theme families**: Default, Ayu, Catppuccin, Gruvbox, Material, Nord, One Dark Pro, Palenight, Rose Pine, Tokyo Night

### django_spire.notification

Notification system with:

- **Notification**: Base notification model
  - title, body, created_datetime

- **EmailNotification**: Email notifications
  - Attachments (File model)
  - CC, BCC support
  - Template ID and context data
  - Size limits: 30MB hard limit, 10MB recommended

- **SMS notifications**: Twilio integration
- **App notifications**: Push-style

### django_spire.profiling

Performance profiling with:

- **ProfilingMiddleware**: Request tracking
- **ProfilingPanel**: Debug toolbar panel
- **Thread locking**: Concurrent access control

### django_spire.ai

AI/LLM integration with:

- Chat system with routers
- Intent-based routing
- Knowledge search integration
- SMS AI integration

## Testing

The `test_project` is a Django project used for testing and demonstrating django_spire framework capabilities. It serves as a sandbox for experimenting with framework features and app integrations.

### Key Features
- Multiple example apps demonstrating framework functionality
- Integration testing environment for django_spire apps
- Template showcase for various UI patterns (tabular, card, modal layouts)
- Seeding and fixture generation examples
- Multiple settings configurations for different environments

### Structure

```
test_project/
├── apps/                     # Example apps demonstrating framework features
│   ├── ai/                   # AI integration examples
│   ├── comment/              # Comment system examples
│   ├── file/                 # File management examples
│   ├── help_desk/            # Help desk examples
│   ├── home/                 # Home/dashboard app
│   ├── infinite_scrolling/   # Infinite scrolling examples
│   ├── lazy_tabs/            # Lazy loading tabs examples
│   ├── notification/         # Notification examples
│   ├── ordering/             # Ordering examples
│   ├── queryset_filtering/   # QuerySet filtering examples
│   ├── tabular/              # Tabular view examples
│   ├── wizard/               # Wizard/step-by-step examples
│   └── model_and_service/    # Model/service pattern examples
├── templates/                # Project-level templates
│   ├── tabular/              # Tabular view templates
│   ├── card/                 # Card view templates
│   ├── modal/                # Modal dialog templates
│   ├── file/                 # File management templates
│   ├── gamification/         # Gamification templates
│   └── form/                 # Form templates
├── static/                   # Static assets (CSS, JS, images, fonts)
├── settings files/           # Multiple environment configurations
│   ├── base_settings.py      # Base settings
│   ├── postgres_settings.py  # PostgreSQL configuration
│   ├── sqlite_settings.py    # SQLite configuration
│   └── dandy_settings.py     # Dandy-specific settings
├── seed.py                   # Main seeding script
├── urls.py                   # Project URL configuration
└── playwright.config.py      # Playwright E2E test configuration
```

### Settings Configuration

**Base Settings** (`base_settings.py`):
- Environment variable configuration via dotenv
- Email configuration (SendGrid)
- SMS notification settings (Twilio)
- AI chat persona configuration
- Maintenance mode
- Debug toolbar integration
- Static file storage (S3/ DigitalOcean)
- Report registry configuration
- Custom auth controllers

**Environment Settings**:
- `postgres_settings.py`: PostgreSQL database configuration
- `sqlite_settings.py`: SQLite for development/testing
- `dandy_settings.py`: Dandy-specific customizations

### Example Apps

#### django_spire.comment Integration
- `CommentExample` model with history tracking and comment mixin
- Seeder for generating test comment data
- Breadcrumb integration
- URL routing at `/comment/`

#### django_spire.lazy_tabs
- Intelligent tab loading with lazy initialization
- Service layer for tab transformation and processing
- Intelligent services for content generation

#### django_spire.help_desk Integration
- Help desk ticket examples
- Priority and status tracking
- Custom seeding

#### django_spire.queryset_filtering
- Advanced QuerySet filtering examples
- Custom report registries
- Task reporting framework

#### django_spire.wizard Integration
- Multi-step wizard examples
- Modal-based wizard flows
- Content progression patterns

### URL Structure

```
/                           # Landing page
/ai/                        # AI integration examples
/comment/                   # Comment examples
/help_desk/                 # Help desk examples
/file/                      # File management examples
/history/                   # History tracking examples
/home/                      # Home/dashboard
/infinite_scrolling/        # Infinite scrolling examples
/lazy_tabs/                 # Lazy tabs examples
/notification/              # Notification examples
/order/                     # Ordering examples
/tabular/                   # Tabular examples
/test_model/                # Model/service examples
/theme/                     # Theme management
/queryset-filtering/        # QuerySet filtering
/wizard/                    # Wizard examples
/django_glue/               # Django Glue integration
/django_spire/              # Django Spire core
/admin/                     # Django admin
```

### Seeding

Run the main seed script to populate test data:
```bash
python test_project/seed.py
```

This seeds:
- Superuser creation
- User data
- API access keys
- Help desk tickets
- QuerySet filtering models
- Infinite scrolling data
- Lazy tabs data
- Comment examples

### Template Patterns

**Tabular Views**:
- `tabular/page/`: Full page layouts
- `tabular/card/`: Card-based layouts
- Supports list, detail, form, and migration views

**Card Views**:
- Card-based grid layouts
- Responsive design patterns
- Mobile-friendly layouts

**Modal Views**:
- Modal dialogs and overlays
- Modal wizard patterns
- Content progression in modals

### Testing

**Playwright E2E Tests**:
- Configuration in `playwright.config.py`
- Browser automation testing
- UI interaction testing

**Pytest Configuration**:
- `pytest.ini` in test_project root
- Test discovery and configuration

### Development

**Running the Project**:
1. Configure environment variables (see `development.env`)
2. Run migrations: `python manage.py migrate`
3. Seed data: `python test_project/seed.py`
4. Start server: `python manage.py runserver`

**Settings Modules**:
- Development: Use `test_project.postgres_settings` or `test_project.sqlite_settings`
- Production: Configure environment variables appropriately

**Static Files**:
- Development: Local storage in `test_project/static/`
- Production: S3/DigitalOcean storage configured via `STORAGES` setting

### Best Practices Demonstrated

1. **Model Mixins**: Use `HistoryModelMixin` and `CommentModelMixin` for automatic tracking
2. **Service Layer**: Keep business logic in service classes, not models
3. **QuerySet Methods**: Custom QuerySet methods for reusable filters
4. **Breadcrumb Integration**: Consistent navigation hierarchy
5. **Template Organization**: Separate templates by view type (tabular, card, modal)
6. **Environment Configuration**: Use environment variables for sensitive data
7. **Seeding**: Use seeders for consistent test data generation
8. **URL Namespacing**: Organize URLs by app with proper namespaces

## Related Documentation

- [Django Spire Docs](https://django-spire.stratusadv.com)
- [Changelog](docs/changelog/changelog.md)
- [Roadmap](docs/roadmap/2025_roadmap.md)
