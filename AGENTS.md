# Agent

## Guidelines
- Always look for relevant skills to load
- Do not comment your code. You should never write anything complicated enough that needs comments.

## Testing Commands

Use the `justfile` for all testing and development commands:

```bash
# Run all tests
just test

# Run tests for a specific app
just test-app django_spire.celery

# Run tests with coverage
just test-coverage

# Run failed tests
just test-failed

# Run Celery worker
just celery

# Run Django server
just run-server

# Run migrations
just migrate

# Make migrations
just make-migrations
```

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
- Notification system for email, SMS, app, and push notifications
- Profiling middleware for performance monitoring
- Tag system with AI-powered tagging
- Intelligence layers across multiple apps for AI-driven features
- Service layer pattern for business logic separation

### Version
- Current: 0.28.7

## Architecture

### Core Structure

```
django_spire/
├── api/                  # API integration (django-ninja)
│   ├── api_v1.py         # API v1 configuration
│   ├── auth/             # API authentication
│   ├── seeding/          # API seeding support
│   ├── urls/             # API URL routing
│   └── views/            # API views
├── ai/                   # AI/LLM integration
│   ├── chat/             # Chat system with routers
│   ├── context/          # Context management
│   ├── prompt/           # Prompt management
│   └── sms/              # SMS AI integration
├── auth/                 # Authentication system (user, group, MFA, permissions)
│   ├── user/             # User management
│   ├── group/            # Group management
│   ├── mfa/              # Multi-factor authentication
│   └── controller/       # Authentication controllers
├── celery/               # Celery task tracking
│   ├── models.py         # CeleryTask model with AsyncResult integration
│   ├── manager.py        # BaseCeleryTaskManager for task management
│   ├── services/         # CeleryTaskService for task result updates
│   ├── querysets.py      # Custom QuerySet methods
│   ├── views/            # Task viewing views
│   ├── urls/             # Task URL routing
│   ├── templatetags/    # Template tags for task widgets
│   └── tests/            # Comprehensive test suite
├── comment/              # Comment system with generic content types
├── contrib/              # Shared utilities and helpers
│   ├── admin/            # Admin utilities
│   ├── breadcrumb/       # Breadcrumb navigation
│   ├── choices/          # Choice utilities
│   ├── constructor/      # Constructor utilities
│   ├── form/             # Form utilities
│   ├── gamification/     # Gamification features
│   ├── generic_views/    # Generic portal views
│   ├── help/             # Help template tags
│   ├── options/          # Options mixins
│   ├── ordering/         # Ordering utilities
│   ├── pagination/       # Pagination utilities
│   ├── performance/      # Performance utilities
│   ├── progress/         # Progress indicators
│   ├── queryset/         # QuerySet utilities
│   ├── responses/        # Response utilities
│   ├── seeding/          # Intelligent field seeders
│   ├── service/          # Base service classes
│   └── session/          # Session controllers
├── core/                 # Core framework functionality
│   ├── tag/              # Tag system with AI intelligence
│   ├── table/            # Table utilities
│   ├── redirect/         # Redirect functionality
│   ├── converters/       # URL converters
│   ├── forms/            # Core forms
│   ├── middleware/       # Core middleware
│   └── management/       # Management commands
│       ├── spire_opencode/    # Opencode integration
│       └── spire_startapp/    # App generation templates
├── file/                 # File management with generic content types
├── help_desk/            # Help desk/ticketing system
├── history/              # Model history and activity tracking
│   ├── activity/         # Activity tracking
│   └── viewed/           # Viewed tracking
├── knowledge/            # Knowledge base management
│   ├── entry/            # Content entries with version history
│   ├── collection/       # Hierarchical organization
│   ├── intelligence/     # Knowledge intelligence layer
│   └── auth/             # Knowledge access control
├── metric/               # Metrics and reporting framework
│   ├── report/           # Reporting framework
│   ├── domain/           # Domain metrics with intelligence
│   └── visual/           # Visual metrics with presentation
├── notification/         # Notification system
│   ├── email/            # Email notifications
│   ├── sms/              # SMS notifications
│   ├── app/              # App notifications
│   └── push/             # Push notifications
├── profiling/            # User profiling and performance monitoring
├── theme/                # Theme management (10+ themes, light/dark modes)
└── urls.py               # Main URL configuration
```

### django_spire.celery

A comprehensive Celery task tracking system with:

**CeleryTask Model** (`celery/models.py`):
- `task_id`: UUID field for Celery task identification
- `task_name`/`display_name`: Task naming
- `reference_key`/`model_key`: Task grouping and association
- `state`: Task state from Celery states
- `async_result`: Property returning AsyncResult for the task
- `has_result`/`_result`: Result storage with pickle serialization
- `is_processing`/`is_failed`/`is_successful`: State boolean properties
- `estimated_completion_*`: Progress estimation properties

**BaseCeleryTaskManager** (`celery/manager.py`):
- Base class for creating task managers
- `task_name`/`display_name`: Class attributes required
- `estimated_completion_seconds`: Optional completion time estimate
- `reference_key`/`model_key`: Key generation from task and model
- `send_task()`: Creates CeleryTask record and sends Celery task

**CeleryTaskService** (`celery/services/service.py`):
- `update_result()`: Updates task result from AsyncResult
- `update_from_async_result_and_save_if_change()`: Syncs state changes

**QuerySet Methods** (`celery/querysets.py`):
- `by_reference_keys()`: Filter by reference keys
- `by_model_keys()`: Filter by model keys
- `by_reference_keys_model_keys()`: Filter by combined keys
- `by_unready()`: Filter by UNREADY_STATES

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
- Sub-apps: auth, seeding, urls, views

### django_spire.ai
AI/LLM integration with:
- **Chat system** (`ai/chat/`):
  - Intent-based routing
  - Knowledge search integration
  - Chat authentication
  - Intelligence layer with decoders and workflows
- **SMS AI** (`ai/sms/`):
  - SMS integration with Twilio
  - Intelligence workflows
- **Context management** (`ai/context/`):
  - Organization prompts
  - Context seeding
- **Prompt management** (`ai/prompt/`):
  - System prompts
  - Prompt tuning
  - Prompt documentation

### django_spire.auth
Authentication system with:
- **AuthUser** (`auth/user/`): Proxy of Django User with activity tracking
- **AuthGroup** (`auth/group/`): Proxy of Django Group with activity tracking
- **MFA** (`auth/mfa/`): Multi-factor authentication (authenticator app, SMS)
- **Permissions**: Permission-based access control
- **AuthController** (`auth/controller/`):
  - BaseAuthController and AppAuthController
  - Custom permission methods (can_add, can_change, can_delete, can_view)
  - Decorator-based permission checking
- Seeding support for auth data

### django_spire.celery
Celery task tracking system with:
- **CeleryTask**: Model for tracking Celery task state and results
  - UUID task_id for task identification
  - State tracking with Celery states
  - Result serialization with pickle
  - Progress estimation properties
  - AsyncResult integration for real-time state
- **BaseCeleryTaskManager**: Manager class for creating task managers
  - Task sending and tracking
  - Reference and model key generation
  - Argument validation
- **CeleryTaskService**: Service for updating task state
  - Result retrieval from AsyncResult
  - State synchronization
- **QuerySet Methods**: Custom filtering methods
  - by_reference_keys, by_model_keys
  - by_reference_keys_model_keys
  - by_unready

### django_spire.comment
Comment system with:
- Generic content-type relationships
- Parent-child relationships (replies)
- User references
- Edit tracking
- Username @mention scraping
- History tracking
- QuerySet with custom methods

### django_spire.file
File management with:
- Generic content-type relationships
- File metadata (name, type, size)
- History tracking
- QuerySet with active filtering
- GenericForeignKey relationships
- Related field tracking

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
- Auth controller for access control

### django_spire.history
History tracking with:
- **HistoryModelMixin**: Automatic history events on save
  - CREATED, UPDATED, DELETED, ACTIVE, INACTIVE, UNDELETED
  - is_active, is_deleted fields
  - history_events GenericRelation
- **ActivityMixin** (`history/activity/`): User action tracking
  - add_activity method
  - verb, information, target fields
- **Viewed tracking** (`history/viewed/`):
  - Tracks model viewing
  - Viewed mixins and models
- HistoryEvent choices: CREATED, UPDATED, DELETED, ACTIVE, INACTIVE, UNDELETED

### django_spire.knowledge
Knowledge base system with:
- **Entry** (`knowledge/entry/`): Content items with version history
  - Services for entry management
  - Converters for data transformation
  - Intelligence layer for content generation
- **Version** (`knowledge/entry/version/`): Different versions of entries
  - Block management
  - Intelligence for markdown formatting
  - Services for version control
- **Block** (`knowledge/entry/version/block/`): Content blocks within versions
  - Data types (list, etc.)
  - Services for block operations
- **Collection** (`knowledge/collection/`): Hierarchical organization
  - Services for collection management
- **Intelligence** (`knowledge/intelligence/`):
  - Bots for content generation
  - Workflows for automation
  - Router for intent handling
- **Auth** (`knowledge/auth/`): Access control for knowledge base

### django_spire.metric
Metrics and reporting framework with:

**Report** (`metric/report/`):
- BaseReport abstract class for custom reports
- Column types: TEXT, NUMBER, DOLLAR, PERCENT (with decimal variants)
- Report rows with formatting options (bold, page breaks, borders)
- Report registry for hierarchical report organization
- ReportRun model for tracking report executions
- Markdown export capability

**Domain** (`metric/domain/`):
- Domain-level metrics and statistics
- Intelligence layer for metric generation
- Seeding for test data
- Services for business logic
- Statistic sub-app for statistical models
- URLs and views for metric display

**Visual** (`metric/visual/`):
- Visual metrics and analytics
- Presentation layer for data visualization
- Signage sub-app for display screens
- Intelligence layer for visual generation
- Seeding for visual test data
- Services for visual processing

### django_spire.notification
Notification system with:

**Base Notification**:
- title, body, created_datetime fields
- Notification managers and querysets

**Email** (`notification/email/`):
- Email notifications with attachments (File model)
- CC, BCC support
- Template ID and context data
- Size limits: 30MB hard limit, 10MB recommended
- SendGrid integration

**SMS** (`notification/sms/`):
- SMS notifications (Twilio integration)
- URLs and views for SMS handling

**App** (`notification/app/`):
- App notifications (push-style within application)
- Separate from push notifications

**Push** (`notification/push/`):
- Push notifications
- Separate from app notifications

**Additional**:
- Automation system for scheduled notifications (`automations.py`)
- Throttling support
- Processors for notification handling
- Choices for notification types

### django_spire.profiling
Performance profiling with:
- ProfilingMiddleware for request tracking
- ProfilingPanel for debug toolbar
- Thread locking for concurrent access
- Templates for profiling display

### django_spire.theme
Theme management with:
- **Theme**: Theme class for configuration
  - from_string() for parsing
  - get_available(), get_default() methods
- **Theme families** (10+):
  1. Default
  2. Ayu
  3. Catppuccin
  4. Gruvbox
  5. Material
  6. Nord
  7. One Dark Pro
  8. Palenight
  9. Rose Pine
  10. Tokyo Night
- Light and dark modes (ThemeMode.LIGHT, ThemeMode.DARK)
- CSS stylesheet generation
- Theme configuration via settings

### django_spire.core
Core framework functionality with:

**Tag System** (`core/tag/`):
- Tag model and management
- Intelligence layer (tag_set_bot.py)
- Service layer for tag operations

**Table Utilities** (`core/table/`):
- Table rendering utilities
- Table templates and components

**Redirect** (`core/redirect/`):
- Redirect functionality
- URL redirection management

**Management Commands**:
- `spire_opencode`: Opencode integration with agents and skills
- `spire_startapp`: App generation templates
- `spire_remove_migration`: Migration cleanup

**Additional**:
- Converters for URL path converters
- Forms for core functionality
- Middleware for core operations
- Static files with theme support
- Extensive template system (accordion, badge, button, card, modal, etc.)

### django_spire.contrib
Shared utilities and helpers:

**Seeding**:
- Intelligent field seeders (static, LLM, custom, callable)
- DjangoModelSeeder for automatic model seeding
- Intelligence bots for automated seeder generation
- Management command: `python manage.py seeding`

**Service** (`contrib/service/`):
- BaseDjangoModelService for business logic
- Separates business logic from models
- Handles field updates with transaction support
- File field deferral for proper model saving

**Generic Views** (`contrib/generic_views/`):
- Portal views for admin UI
- detail_view, list_view, form_view, delete_form_view
- Breadcrumb integration
- Activity tracking

**Admin** (`contrib/admin/`):
- SpireModelAdmin for automatic admin configuration
- Auto-configures list_display, list_filter, search_fields
- Read-only fields for created_datetime, is_active, is_deleted

**Breadcrumb** (`contrib/breadcrumb/`):
- Breadcrumbs system
- add_breadcrumb, add_obj_breadcrumb methods
- Integration with portal views

**Choices** (`contrib/choices/`):
- Choice utilities and helpers

**Constructor** (`contrib/constructor/`):
- Constructor utilities

**Form** (`contrib/form/`):
- Form utilities with templates

**Gamification** (`contrib/gamification/`):
- Gamification features
- Static files and templates

**Options** (`contrib/options/`):
- Options mixins

**Ordering** (`contrib/ordering/`):
- Ordering utilities with services

**Pagination** (`contrib/pagination/`):
- Pagination utilities with templatetags

**Performance** (`contrib/performance/`):
- Performance utilities

**Progress** (`contrib/progress/`):
- Progress indicators with static files and templates

**QuerySet** (`contrib/queryset/`):
- QuerySet utilities

**Responses** (`contrib/responses/`):
- Response utilities

**Session** (`contrib/session/`):
- Session controllers

**Help** (`contrib/help/`):
- Help template tags

## Technology Stack

- **Backend**: Python, Django 5.1+
- **API Framework**: django-ninja (async-ready, Pydantic-based)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: PostgreSQL
- **Storage**: AWS S3 / DigitalOcean
- **Email**: SendGrid
- **SMS**: Twilio
- **Task Queue**: Celery

## Core Design Patterns

### Intelligence Layer Pattern
Many apps include an intelligence layer for AI-driven features:
- `ai/chat/intelligence/`: Decoders, workflows
- `ai/sms/intelligence/`: Workflows
- `knowledge/intelligence/`: Bots, workflows, router
- `metric/domain/intelligence/`: Bots, workflows
- `metric/visual/intelligence/`: Bots, workflows
- `core/tag/intelligence/`: Tag set bot

### Service Layer Pattern
Business logic is separated into service classes:
- `contrib/service/`: BaseDjangoModelService
- `knowledge/entry/services/`
- `knowledge/collection/services/`
- `help_desk/services/`
- `metric/domain/services/`
- `metric/visual/services/`
- `auth/user/services/`
- `celery/services/`: CeleryTaskService

### Auth Sub-App Pattern
Many apps include dedicated auth sub-apps:
- `knowledge/auth/`
- `help_desk/auth/`
- `api/auth/`
- `ai/chat/auth/`

### Seeding Support Pattern
Most major apps include seeding support:
- `knowledge/seeding/`
- `ai/context/seeding/`
- `metric/domain/seeding/`
- `metric/visual/seeding/`
- `auth/seeding/`
- `api/seeding/`

## Testing

The `test_project` is a Django project used for testing and demonstrating django_spire framework capabilities. It serves as a sandbox for experimenting with framework features and app integrations.

### Key Features
- Multiple example apps demonstrating framework functionality
- Integration testing environment for django_spire apps
- Template showcase for various UI patterns (tabular, card, modal layouts)
- Seeding and fixture generation examples
- Multiple settings configurations for different environments
- Celery example app with task managers and views

### Structure

```
test_project/
├── apps/                     # Example apps demonstrating framework features
│   ├── ai/                   # AI integration examples
│   ├── celery/               # Celery task tracking examples
│   ├── comment/              # Comment system examples
│   ├── core/                 # Core context processors
│   ├── file/                 # File management examples
│   ├── help_desk/            # Help desk examples
│   ├── history/              # History tracking examples
│   ├── home/                 # Home/dashboard app
│   ├── infinite_scrolling/   # Infinite scrolling examples
│   ├── knowledge/            # Knowledge base examples
│   ├── landing/              # Landing page app
│   ├── lazy_tabs/            # Lazy loading tabs examples
│   ├── model_and_service/    # Model/service pattern examples
│   ├── notification/         # Notification examples
│   ├── ordering/             # Ordering examples
│   ├── queryset_filtering/   # QuerySet filtering examples
│   ├── tabular/              # Tabular view examples
│   └── wizard/               # Wizard/step-by-step examples
├── celery/                   # Celery example implementation
│   ├── celery/               # Celery tasks and managers
│   │   ├── tasks.py          # Shared tasks (pirate_noise_task, etc.)
│   │   └── managers.py       # Task managers (PirateSongCeleryTaskManager, etc.)
│   ├── views.py              # Example views
│   └── urls.py               # URL routing
├── templates/                # Project-level templates
│   ├── ai/
│   ├── breadcrumb/
│   ├── celery/               # Celery templates
│   ├── comment/
│   ├── django_spire/
│   ├── file/
│   ├── form/
│   ├── gamification/
│   ├── help/
│   ├── help_desk/
│   ├── history/
│   ├── home/
│   ├── infinite_scrolling/
│   ├── landing/
│   ├── lazy_tabs/
│   ├── maintenance/
│   ├── modal/
│   │   ├── content/
│   │   ├── page/
│   │   ├── modal.html
│   │   └── modal_wizard.html
│   ├── model_and_service/
│   ├── notification/
│   ├── options/
│   ├── ordering/
│   ├── pagination/
│   ├── permission/
│   ├── queryset_filtering/
│   ├── search/
│   ├── tabular/
│   │   ├── card/
│   │   ├── form/
│   │   ├── item/
│   │   ├── modal/
│   │   ├── page/
│   │   └── table/
│   ├── user_account/
│   │   └── profile/
│   └── wizard/
├── static/                   # Static assets (CSS, JS, images, fonts)
├── settings files/           # Multiple environment configurations
│   ├── base_settings.py      # Base settings
│   ├── postgres_settings.py  # PostgreSQL configuration
│   ├── sqlite_settings.py    # SQLite configuration
│   └── dandy_settings.py     # Dandy-specific settings
├── seed.py                   # Main seeding script
├── urls.py                   # Project URL configuration
├── playwright.config.py      # Playwright E2E test configuration
├── pytest.ini                # Pytest configuration
├── worker.py                 # Worker process configuration
├── asgi.py                   # ASGI configuration
└── wsgi.py                   # WSGI configuration
```

### Settings Configuration

**Base Settings** (`base_settings.py`):
- Environment variable configuration via dotenv
- Email configuration (SendGrid)
- SMS notification settings (Twilio)
- AI chat persona configuration
- Maintenance mode
- Debug toolbar integration
- Static file storage (S3/DigitalOcean)
- Report registry configuration
- Custom auth controllers

**Environment Settings**:
- `postgres_settings.py`: PostgreSQL database configuration
- `sqlite_settings.py`: SQLite for development/testing
- `dandy_settings.py`: Dandy-specific customizations

### Example Apps

#### django_spire.celery Integration
- `CeleryTask` model with AsyncResult integration
- `BaseCeleryTaskManager` subclasses for task management
- Views for task display (item, toast, list views)
- Template tags for task widgets
- URL routing at `/celery/task/`
- Example app in `test_project/app/celery/`:
  - `celery/tasks.py`: Example tasks (pirate_noise_task, ninja_attack_task, etc.)
  - `celery/managers.py`: Example managers (PirateSongCeleryTaskManager, NinjaAttackCeleryTaskManager)

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

#### django_spire.infinite_scrolling
- Infinite scrolling pagination examples
- AJAX-based content loading

#### django_spire.ordering
- Model ordering examples
- Drag-and-drop ordering
- Custom ordering services

#### django_spire.model_and_service
- Model/service pattern examples
- Business logic separation
- Service layer implementation

### URL Structure

```
/                           # Landing page (landing app)
celery/                     # Celery examples
├── celery/home/            # Celery home view
django_spire/celery/        # Celery framework
├── django_spire/celery/task/item/<task_id>/      # Single task view
├── django_spire/celery/task/item_list/           # Task list view
├── django_spire/celery/task/toast/<task_id>/     # Toast task view
└── django_spire/celery/task/toast_list/          # Toast list view
/ai/                        # AI integration examples
/comment/                   # Comment examples
/help_desk/                 # Help desk examples
/file/                      # File management examples
/history/                   # History tracking examples
/home/                      # Home/dashboard
/infinite_scrolling/        # Infinite scrolling examples
/knowledge/                 # Knowledge base examples
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
- User data (django_spire.auth)
- API access keys (django_spire.api)
- Help desk tickets
- QuerySet filtering models
- Infinite scrolling data
- Lazy tabs data
- Comment examples
- Celery task tracking examples

**Optional seeding** (commented out in seed.py):
- Knowledge data (django_spire.knowledge)
- AI context data (django_spire.ai.context)

### Test File Structure

Tests follow the Django testing best practices with the following structure:

```
django_spire/
├── celery/
│   └── tests/
│       ├── __init__.py
│       ├── factories.py              # create_test_celery_task factory
│       ├── test_models.py            # CeleryTask model tests
│       ├── test_views.py             # View tests
│       ├── test_urls.py              # URL routing tests
│       ├── test_querysets.py         # QuerySet method tests
│       ├── test_templatetags.py      # Template tag tests
│       ├── test_async_result_integration.py  # AsyncResult integration tests
│       ├── test_services/
│       │   ├── __init__.py
│       │   └── test_celery_task_service.py    # Service tests
│       └── test_managers/
│           ├── __init__.py
│           └── test_base_celery_task_manager.py # Manager tests
```

### Testing Best Practices

1. **Factory Pattern**: Use `create_test_celery_task()` factory for all test data
2. **AsyncResult Mocking**: Use `@patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)` for AsyncResult tests
3. **Service Testing**: Test service methods with mocked AsyncResult interactions
4. **View Testing**: Use `RequestFactory` and mock `get_object_or_404`
5. **QuerySet Testing**: Test custom QuerySet methods with filtered results
6. **State Transitions**: Test state change logic (PENDING → STARTED → SUCCESS/FAILURE)

### Playwright E2E Tests

- Configuration in `playwright.config.py`
- Browser automation testing
- UI interaction testing

### Pytest Configuration

- `pytest.ini` in test_project root
- Test discovery and configuration
- Custom markers for app-specific tests

### Development

**Running the Project**:
1. Configure environment variables (see `development.env`)
2. Run migrations: `just migrate`
3. Seed data: `python test_project/seed.py`
4. Start server: `just run-server`

**Running Tests**:
1. Run all tests: `just test`
2. Run Celery tests: `just test celery`
3. Run with coverage: `just test-coverage`

**Running Celery Worker**:
```bash
just celery
```

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
9. **Intelligence Layer**: Implement AI-driven features through intelligence sub-apps
10. **Auth Sub-apps**: Separate access control into dedicated auth sub-apps
11. **AsyncResult Integration**: Comprehensive testing of Celery AsyncResult interactions

### Recommended Example Apps to Add

The following framework components could benefit from dedicated example apps:
- `django_spire.metric` (reporting framework)
- `django_spire.auth` (authentication patterns)
- `django_spire.api` (API usage examples)
- `django_spire.theme` (theme customization)
- `django_spire.profiling` (performance profiling)

## Related Documentation

- [Django Spire Docs](https://django-spire.stratusadv.com)
- [Changelog](docs/changelog/changelog.md)
- [Roadmap](docs/roadmap/2025_roadmap.md)