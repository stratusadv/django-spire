# Help Desk Tickets

> **Purpose:** Provide a centralized ticket system for tracking app and company issues, with priority and status lifecycle management, a service layer for creation, and automatic notifications to developers and managers.

---

## Why Help Desk?

Support requests and internal issues need a structured home. **The Help Desk system** provides:

- A single `HelpDeskTicket` model for both app and company issues
- Priority and status lifecycle to move tickets from triage to resolution
- A service layer that handles creation and triggers notifications automatically
- Role-based access control using Django's permission system
- Built-in list, detail, create, and update views ready to use

---

## Quick Start

### 1. Add the App

Add `django_spire.help_desk` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_spire.help_desk',
]
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Create a Ticket

Always create tickets through the service layer so notifications are triggered automatically:

```python
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.choices import (
    HelpDeskTicketPurposeChoices,
    HelpDeskTicketPriorityChoices,
)

ticket = HelpDeskTicket()

ticket.services.create(
    created_by=request.user,
    purpose=HelpDeskTicketPurposeChoices.APP,
    priority=HelpDeskTicketPriorityChoices.HIGH,
    description='The dashboard fails to load when filtering by date range.',
)
```

---

## Core Concepts

### The `HelpDeskTicket` Model

The single model representing a support or issue ticket.

```python
from django_spire.help_desk.models import HelpDeskTicket
```

Key fields:

| Field | Description |
|---|---|
| `created_by` | The user who submitted the ticket (`User` FK, set automatically by the service) |
| `purpose` | Whether the issue is app-related or company-related |
| `priority` | Urgency level: `low`, `medium`, `high`, or `urgent` |
| `status` | Lifecycle state: `ready` → `in_progress` → `done` (default: `ready`) |
| `description` | Full description of the issue |

### Choices

**Purpose** — what the ticket is about:

| Value | Display |
|---|---|
| `app` | App |
| `comp` | Company |

**Priority** — how urgently it needs attention:

| Value | Display |
|---|---|
| `low` | Low |
| `med` | Medium |
| `high` | High |
| `urge` | Urgent |

**Status** — where the ticket is in the resolution workflow:

| Value | Display |
|---|---|
| `read` | Ready |
| `prog` | In Progress |
| `done` | Done |

### The `HelpDeskTicketService`

Accessed on any `HelpDeskTicket` instance via `ticket.services`. The service layer is the recommended way to create tickets — it sets `created_by`, saves the ticket, and fires notifications in one call.

```python
ticket.services.create(created_by=user, **kwargs) -> HelpDeskTicket
```

---

## Main Operations

### Creating a Ticket

Always use `ticket.services.create()` rather than `HelpDeskTicket.objects.create()` directly. The service ensures `created_by` is set and notifications are dispatched.

```python
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.choices import (
    HelpDeskTicketPurposeChoices,
    HelpDeskTicketPriorityChoices,
)

ticket = HelpDeskTicket()

ticket.services.create(
    created_by=request.user,
    purpose=HelpDeskTicketPurposeChoices.COMPANY,
    priority=HelpDeskTicketPriorityChoices.URGENT,
    description='Payroll data is not syncing with the accounting system.',
)
```

### Querying Tickets

```python
from django_spire.help_desk.models import HelpDeskTicket

# All active tickets, newest first
tickets = HelpDeskTicket.objects.order_by('-created_datetime').active()

# A single ticket
ticket = HelpDeskTicket.objects.get(pk=1)
```

### Updating a Ticket

Use the standard Django form or update fields directly and save:

```python
from django_spire.help_desk.choices import HelpDeskTicketStatusChoices

ticket = HelpDeskTicket.objects.get(pk=1)
ticket.status = HelpDeskTicketStatusChoices.INPROGRESS
ticket.save()
```

---

## Permissions

Access to ticket views is controlled by Django model permissions on `HelpDeskTicket`. Assign these to users or groups as needed.

| Permission | Codename | Description |
|---|---|---|
| Add | `add_helpdeskticket` | Create new tickets |
| Change | `change_helpdeskticket` | Edit existing tickets |
| Delete | `delete_helpdeskticket` | Delete tickets (also grants manager notifications) |
| View | `view_helpdeskticket` | View ticket list and detail |

> Users with `delete_helpdeskticket` are treated as **managers** by the notification service and receive in-app notifications for all new tickets. See the [Notifications](notifications.md) guide for details.

---

## Built-in URLs

The help desk app registers its own URLs automatically when included via `URLPATTERNS_INCLUDE`. The available routes are:

| View | URL Pattern | Name |
|---|---|---|
| Ticket list | `help_desk/page/list/` | `django_spire:help_desk:page:list` |
| Ticket detail | `help_desk/page/<pk>/detail/` | `django_spire:help_desk:page:detail` |
| Ticket delete | `help_desk/page/<pk>/delete/` | `django_spire:help_desk:page:delete` |
| Create form | `help_desk/form/create/` | `django_spire:help_desk:form:create` |
| Update form | `help_desk/form/<pk>/update/` | `django_spire:help_desk:form:update` |
