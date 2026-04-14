---
name: service-layer
description: Service layer best practices on django models 
---

# Service Layer Best Practices

## Important: Coding Standards

**No Docstrings or Comments:** This skill follows the project's python-style guidelines. NEVER add docstrings to functions, methods, or classes. NEVER add comments (inline or block). Code must be self-explanatory through clear naming and type hints only. See the `python-style` skill for complete guidelines.

## Purpose

The service layer provides each domain model with a predictable "service layer" so that business rules live next to the data and can be invoked as naturally as `Task.objects`.

## 1. Why a Service Layer?

Django's flexibility often scatters business logic across views, utils, managers, and helpers. A dedicated service layer centralizes business rules by pinning them to the model that owns them. Each model exposes a services descriptor that:

- Groups validation, persistence, and side-effects in one place
- Provides easy access from model: `task.services.notification.send_created()`
- Keeps code modular for easy testing
- Avoids circular-import headaches through proper use of future annotations and TYPE_CHECKING guards

### Example:

The example below demonstrates using a simple Task model to showcase service layer functionality:

## 2. What the BaseService Provides

### BaseDjangoModelService Methods

| Method | Purpose |
|--------|---------|
| `validate_model_obj()` | Runs full_clean() on the target object and raises if validation fails. |
| `save_model_obj(**field_data)` | Calls validate_model_obj() and then save(). This is the primary pipeline used for saving objects. Avoid calling form.save() or object.save() directly; pass everything through save_model_obj() to maintain a controlled pipeline for model persistence. Returns a tuple `(obj, is_created)`. |

**Service Pipeline Pattern:**

By channeling all persistence through `save_model_obj()`, developers ensure that:
- All Request Noise (versioning, metadata, etc.) is routed only through this control path.
- Any advanced state (eg. decoration, pagination, sort conditions) is processed in a single place.

**Using save_model_obj():**

Always use `save_model_obj()` with named field parameters instead of setting attributes and calling `.save()`:

```python
# ❌ Avoid: Direct attribute setting and save
company_user.is_active = True
company_user.save()

# ✅ Prefer: Using save_model_obj with field names
obj, is_created = company_user.services.save_model_obj(is_active=True)
return obj
```

This ensures validation and any request noise handling is properly applied.

## 3. Building a Service

### 3.1 Files & Directory Structure

```
tasks/
├── models.py
└── services/
    ├── service.py              # TaskService (primary)
    └── notification_service.py  # TaskNotificationService (secondary)
```

### 3.2 The Model

```python
# tasks/models.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from app.tasks.services.service import TaskService

class Task(models.Model):
    title = models.CharField(max_length=200)
    is_done = models.BooleanField(default=False)
    
    services = TaskService()
    
    def __str__(self) -> str:
        return self.title
```

### 3.3 The Service

```python
# tasks/services/service.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from app.tasks.models import Task
    from app.tasks.services.notification_service import TaskNotificationService
    from app.tasks.services.processor_service import TaskProcessorService

class TaskService(BaseDjangoModelService['Task']):
    # target model — must be declared first
    obj: Task    

    # followed by all sub-services that are related to the model
    notification = TaskNotificationService()
    processor = TaskProcessorService()
```

## 4. Common Service Files: Judgement-Based Approach

The table below outlines the typical file structure and responsibilities within the service layer:

| File Path | Class | Responsibility |
|-----------|-------|----------------|
| services/service.py | TaskService | Parent service that composes sub-services and exposes high-level operations |
| services/notification_service.py | TaskNotificationService | Notifications, messaging, and side-effect integrations (e.g., emails, webhooks) |
| services/processor_service.py | TaskProcessorService | Core task processing logic and workflows |
| services/transformation_service.py (optional) | TaskTransformationService | Data transforms or enrichment supporting other services |

Each service should define the target object type (e.g., `obj: Task`) for instance-level operations and may also provide class-level utilities for bulk or maintenance tasks. Keep responsibilities focused and cohesive.

## 5. Class- vs Instance-Level Access

```python
from app.tasks.models import Task

# Instance-level usage – operate on one concrete record
task = Task.objects.get(pk=42)
after = task.services.mark_done()

# Class-level usage – when no specific record rows exist, uses "null" task (pk = None)
Task.services.automation.clean_dead_tasks()
```

### When to Use Each Approach:

| Use-Case | Call form | Rationale |
|----------|-----------|-----------|
| Work on one existing row in db | `task.services.mark_done()` | Direct operations on instance, mutate and persist changes. |
| Run bulk/maintenance logic when no row exists yet | `Task.services.automation.clean_dead_tasks()` | Utilizes natural behavior without specific task, service creates temporary task containment for behavior. |

## 6. Accessing Model Class in Service

When embedded within a service layer, access to the model class is available for database queries and manipulations. Service initialization sets the model class as an attribute matching the model name. In the background, our base service sets the target object class as the attribute by the given class name.

### Pattern Usage:

```python
# tasks/services/service.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from app.tasks.models import Task

class TaskAutomationService(BaseDjangoModelService['Task']):    
    obj: Task

    def mark_stale(self) -> Task:
        stale_tasks = self.obj_class.objects.filter(created_date__lte='2020-01-01')
        # ...
```

The service layer inherits from a base class that exposes `obj_class`, giving you access to the model class for queries and bulk operations. Use this for marking, processing, or reversing events at runtime as necessary for asset management and orchestration.

## 7. Handling Complex Services

As services grow, it’s acceptable—and often desirable—to keep small, private helper methods inside the service to support readability and cohesion. When the logic becomes complex or domain-rich, extract that logic into a dedicated class (or small class cluster) placed in a subdirectory of the related app, and let the service compose and orchestrate it.

### 7.1 Private helpers inside a service

Keep simple, service-specific helpers private to the file. Use a leading underscore to signal intent.

```python
# tasks/services/processor_service.py
from __future__ import annotations
from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from app.tasks.models import Task

class TaskProcessorService(BaseDjangoModelService['Task']):
    obj: Task

    def mark_done(self) -> Task:
        self._ensure_can_mark_done()
        self.obj.is_done = True
        return self.save_model_obj()

    # private, service-local validation
    def _ensure_can_mark_done(self) -> None:
        if not self.obj.title:
            raise ValueError("Cannot mark done without a title")
```

### 7.2 Automation services orchestrating notifications

When recurring workflows or time-based checks are needed (e.g., scanning for overdue tasks and notifying users), model-scoped automation services are a good fit. They coordinate queries and delegate messaging to a notification service.

Recommended layout:

```
tasks/
├── models.py
└── services/
    ├── service.py                 # TaskService (orchestrator/parent)
    ├── notification_service.py    # TaskNotificationService (emails, webhooks, etc.)
    └── automation_service.py      # TaskAutomationService (overdue scans, scheduled jobs)
```

Implementation sketch (pseudocode):

```python
# tasks/services/automation_service.py
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable
from django.utils import timezone
from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from app.tasks.models import Task
    from app.tasks.services.notification_service import TaskNotificationService


class TaskAutomationService(BaseDjangoModelService['Task']):
    obj: Task  # instance when called from an object; null-like when invoked at class-level

    # composed sub-service; defined on TaskService in service.py
    notification: TaskNotificationService

    def send_overdue_notifications(self, *, as_of=None) -> int:
        now = as_of or timezone.now()
        # Example criteria; adjust to your schema (due_at/assignee/status, etc.)
        overdue_qs = self.obj_class.objects.filter(is_done=False, due_at__lt=now)

        sent = 0
        for batch in self._batched(overdue_qs.iterator(), size=200):  # avoid loading everything at once
            for t in batch:
                # Delegate the actual message send to the notification service
                self.notification.send_overdue(t)
                sent += 1
        return sent

    # Private batching helper for memory-safe iteration
    def _batched(self, items: Iterable, size: int):
        batch = []
        for item in items:
            batch.append(item)
            if len(batch) == size:
                yield batch
                batch = []
        if batch:
            yield batch
```

### 7.3 Usage from views or jobs (unchanged boundary)

Views and jobs should call the service layer; services orchestrate notifications. For bulk automations, prefer class-level calls (e.g., from a management command or scheduled job):

```python
# management command or scheduled job
from app.tasks.models import Task

def run_overdue_job():
    sent = Task.services.automation.send_overdue_notifications()
    print(f"Sent {sent} overdue notifications")
```

You can still expose instance-level helpers for one-off actions when appropriate:

```python
def mark_and_notify_view(request, pk: int):
    task = Task.objects.get(pk=pk)
    if not task.is_done:
        task.services.processor.mark_done()
        task.services.notification.send_completed(task)
```

### 7.4 Guidelines

- Start with private helpers inside services; introduce an automation service when workflows are time-based, periodic, or span multiple queries.
- Keep orchestration (queries, batching, retries, handoffs) in services; keep pure formatting of messages inside notification service methods.
- Prefer class-level automation methods for scans across many rows; instance-level for single-record workflows.
- Tests: unit-test notification formatting separately; integration-test automation methods to ensure correct query and delegation.

### 7.5 Naming guidance

- **Path Readability**: Method names should read like natural English when chained. The full path `Model.services.subservice.method()` should clearly explain what is happening.
  - ✅ `CompanyUser.services.factory.create_or_activate()` - Clear, reads like English
  - ❌ `CompanyUser.services.factory.get_or_create_for_company_user()` - Technical pattern, less readable
  
- **Business Intent Over Technical Pattern**: Name methods to describe the business action and outcome, not just the implementation pattern.
  - ✅ `create_or_activate` - Describes what happens: create new or activate existing
  - ❌ `get_or_create` - Describes the Django pattern, not the business intent

- **Keep automation under services/** as a peer to notification and processor services.
- Views, jobs, and commands should call the service layer: Task.services.automation.send_overdue_notifications().

### Best Practices Checklist

1. **Use Future Annotations**: Always use `from __future__ import annotations` at the top of service files
2. **TYPE_CHECKING Guards**: Surround imports with `if TYPE_CHECKING:` blocks to avoid circular imports
3. **Service Structure**: Maintain predictable naming patterns for easy discovery
4. **Documentation**: Document interfaces for complex service interactions
5. **Isolation**: Extend a single instance across service stack using gather states utilities when possible
6. **Consistency**: Always ensure restore type stability using service decorator for validation and interaction

## Service Types and Responsibilities

### Factory Services
**Purpose:** Create and initialize model instances with complex dependencies

**Pattern:**
```python
class EpisodeFactoryService(BaseDjangoModelService['Episode']):
    obj: Episode
    
    def upload(self, podcast: Podcast, audio_file_path: Path):
        # 1. Create related objects
        transcription = Transcription.services.factory.create_from_audio_file_path(audio_file_path)
        
        # 2. Create main object
        self.obj.services.save_model_obj(
            podcast=podcast,
            transcription=transcription,
            name=audio_file_path.name.split('.')[0],
            audio_file_path=audio_file_path,
            episode_number=podcast.episodes.all().count() + 1
        )
        
        # 3. Trigger transformations
        self.obj.services.transformation.to_wav()
        
        # 4. Create downstream objects
        KeyConcept.services.factory.create_from_episode(self.obj)
        
        return self.obj

class CompanyUserFactoryService(BaseDjangoModelService['CompanyUser']):
    obj: CompanyUser
    
    def create_or_activate(self, company: Company, user: User) -> CompanyUser:
        try:
            company_user = self.obj_class.objects.get(company=company, user=user)
            obj, is_created = company_user.services.save_model_obj(is_active=True)
            return obj
        except self.obj_class.DoesNotExist:
            return self.obj_class.objects.create(company=company, user=user)
```

**Key Points:**
- Always use `save_model_obj()` for persistence (not direct `.save()`)
- Pass field names as parameters: `save_model_obj(is_active=True)`
- Always unpack the tuple: `obj, is_created = ...`
- Chain transformations after creation
- Create downstream objects as needed
- Return the created instance
- **Name methods for path readability**: `create_or_activate` reads clearly in English

### Intelligence Services
**Purpose:** Process data using AI/LLM workflows

**Pattern:**
```python
class EpisodeIntelligenceService(BaseDjangoModelService['Episode']):
    obj: Episode
    
    def generate_details(self) -> EpisodeIntel:
        details_intel = bots.EpisodeBot().process(self.obj)
        return details_intel
    
    def find_quotes(self) -> EpisodeQuotesIntel:
        details_intel = bots.EpisodeQuoteBot().process(self.obj)
        return details_intel
```

**Key Points:**
- Use bot/intelligence classes for AI processing
- Return typed intel objects
- Keep methods focused on single intelligence tasks

### Transformation Services
**Purpose:** Convert data between formats or create derived files

**Pattern:**
```python
class EpisodeTransformationService(BaseDjangoModelService['Episode']):
    obj: Episode
    
    def to_wav(self):
        audio = AudioSegment.from_file(self.obj.audio_path, format="m4a")
        audio.export(
            self.obj.audio_path.with_name(f'{self.obj.audio_path.stem}.wav'),
            format="wav"
        )
    
    def to_audacity_labels(self) -> str:
        labels = "".join([
            k.services.transformation.to_audacity_label()
            for k in self.obj.key_concepts.all()
        ])
        
        file_path = self.obj.audio_path.with_name('audacity_labels.txt')
        
        with open(file_path.absolute(), "w") as f:
            f.write(labels)
        
        return labels
```

**Key Points:**
- Work with file systems and data conversion
- Can return transformed data or file paths
- Often work with related objects
- Clean up created files in tests

### Processor Services
**Purpose:** Handle data processing, queries, and business logic

**Pattern:**
```python
class TranscriptionProcessorService(BaseDjangoModelService['Transcription']):
    obj: Transcription
    
    @staticmethod
    def transcribe_audio(audio_file_path: Path) -> AudioChunker:
        with AudioChunker(audio_file_path) as chunker:
            chunker.to_chunks()
        
        for chunk in chunker:
            chunk.transcribe()
        
        return chunker
    
    def find_chunk(self, start_seconds: float, end_seconds: float) -> str:
        words = self.obj.words.filter(
            start_seconds__gte=start_seconds,
            end_seconds__lte=end_seconds,
        )
        return ' '.join([w.text for w in words])
```

**Key Points:**
- Use `@staticmethod` for class-level operations
- Use instance methods for object-specific operations
- Handle complex business logic
- Perform database queries efficiently

## Service Layer Testing Patterns

### Test Structure
```python
from __future__ import annotations
from django_spire.core.tests.test_cases import BaseTestCase
from unittest.mock import Mock, patch

from app.podcast.episode.tests.factories import create_test_episode
from app.podcast.tests.factories import create_test_podcast
from app.transcription.tests.factories import create_test_transcription


class EpisodeServiceTransformationTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.podcast = create_test_podcast()
        self.transcription = create_test_transcription()
        self.episode = create_test_episode(
            podcast=self.podcast,
            transcription=self.transcription
        )
    
    def test_to_wav(self):
        self.episode.services.transformation.to_wav()
        original_path = self.episode.audio_path
        new_file = Path(original_path).with_suffix('.wav')
        self.assertTrue(new_file.exists())
        new_file.unlink()  # Clean up
    
    def test_to_audacity_labels(self):
        self.episode.services.transformation.to_audacity_labels()
        original_path = self.episode.audio_path
        new_file = Path(original_path).with_name('audacity_labels.txt')
        self.assertTrue(new_file.exists())
        new_file.unlink()  # Clean up
```

### Testing Factory Services
```python
class EpisodeServiceFactoryTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.podcast = create_test_podcast()
        self.transcription = create_test_transcription()
    
    @patch('app.transcription.services.processor_service.TranscriptionProcessorService.transcribe_audio')
    def test_upload(self, mock_transcribe_audio):
        # Mock expensive operations
        mock_chunker = create_test_audio_chunker()
        mock_transcribe_audio.return_value = mock_chunker
        
        episode = Episode.services.factory.upload(
            podcast=self.podcast,
            audio_file_path=test_audio_file_path()
        )
        
        self.assertIsNotNone(episode)
        self.assertIsNotNone(episode.transcription)
        self.assertGreater(episode.transcription.words.count(), 0)
        self.assertGreater(episode.transcription.segments.count(), 0)
```

### Testing Intelligence Services
```python
class EpisodeServiceIntelligenceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.episode = create_test_episode(
            podcast=create_test_podcast(),
            transcription=create_test_transcription()
        )
    
    def test_generate_details(self):
        details = self.episode.services.intelligence.generate_details()
        self.assertIsNotNone(details)
        # Assert specific properties of details
```

### Testing Processor Services
```python
class TranscriptionServiceProcessorTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.transcription = create_test_transcription()
    
    def test_find_chunk(self):
        chunk = self.transcription.services.processor.find_chunk(2, 100)
        self.assertIsNotNone(chunk)
        self.assertIsInstance(chunk, str)
```

## Common Service Patterns

### Pattern 1: Chained Transformations
```python
def upload(self, podcast: Podcast, audio_file_path: Path):
    # Create transcription
    transcription = Transcription.services.factory.create_from_audio_file_path(audio_file_path)
    
    # Create episode
    self.obj.services.save_model_obj(
        podcast=podcast,
        transcription=transcription,
        name=audio_file_path.name.split('.')[0],
        audio_file_path=audio_file_path,
        episode_number=podcast.episodes.all().count() + 1
    )
    
    # Chain transformations
    self.obj.services.transformation.to_wav()
    KeyConcept.services.factory.create_from_episode(self.obj)
    self.obj.services.transformation.to_audacity_labels()
    
    return self.obj
```

### Pattern 2: Static vs Instance Methods
```python
class TranscriptionProcessorService(BaseDjangoModelService['Transcription']):
    obj: Transcription
    
    # Class-level operation (no specific instance)
    @staticmethod
    def transcribe_audio(audio_file_path: Path) -> AudioChunker:
        # Use AudioChunker directly, not self.obj
    
    # Instance-level operation (specific instance)
    def find_chunk(self, start_seconds: float, end_seconds: float) -> str:
        # Use self.obj for queries
        words = self.obj.words.filter(...)
```

### Pattern 3: Service Composition
```python
class EpisodeService(BaseDjangoModelService['Episode']):
    obj: Episode
    
    # Compose sub-services
    factory = EpisodeFactoryService()
    transformation = EpisodeTransformationService()
    intelligence = EpisodeIntelligenceService()
```

### Pattern 4: Private Helpers
```python
class EpisodeTransformationService(BaseDjangoModelService['Episode']):
    obj: Episode
    
    def to_audacity_labels(self) -> str:
        labels = self._generate_labels()
        self._write_labels_file(labels)
        return labels
    
    def _generate_labels(self) -> str:
        return "".join([
            k.services.transformation.to_audacity_label()
            for k in self.obj.key_concepts.all()
        ])
    
    def _write_labels_file(self, labels: str):
        file_path = self.obj.audio_path.with_name('audacity_labels.txt')
        with open(file_path.absolute(), "w") as f:
            f.write(labels)
```

## Service Layer Development Workflow

### Step 1: Identify Service Type
- **Factory**: Creating new instances with complex setup
- **Intelligence**: AI/LLM processing and analysis
- **Transformation**: Data conversion and file generation
- **Processor**: Business logic and data processing

### Step 2: Create Service File
- Follow naming: `{service_type}_service.py`
- Use `from __future__ import annotations`
- Add `TYPE_CHECKING` guards
- Inherit from `BaseDjangoModelService['ModelName']`

### Step 3: Define Service Methods
- One method per responsibility
- **Clear, English-like names**: Method names should read naturally in the full call path (e.g., `create_or_activate` not `get_or_create_for_user`)
- **Business intent over technical pattern**: Choose names that describe what happens, not how it's implemented
- **Use `save_model_obj(**field_data)`**: Always pass field names as parameters and unpack the tuple: `obj, is_created = obj.services.save_model_obj(field=value)`
- Proper type hints

### Step 4: Compose in Main Service
- Add to `service.py` as sub-services
- Order: factory, transformation, intelligence, processor
- Maintain consistent naming

### Step 5: Write Tests
- Create test file: `test_{service_type}_service.py`
- Use factories for test data
- Mock expensive operations
- Clean up created files
- Run tests with `test-app` tool
- Fix until all tests pass

### Step 6: Document
- Add docstrings for complex methods
- Document return types
- Note any side effects