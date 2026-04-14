---
name: testing
description: Best practices for writing Django tests (updated template)
---

# Django Testing Best Practices

## Overview

This skill outlines testing conventions and best practices for Django applications. Tests should focus on verifying business logic outcomes rather than framework functionality.

### When to Use
- Writing new test cases for models, services, and views
- Creating test factories for test data generation
- Reviewing existing test code for quality and compliance
- Setting up test infrastructure for new apps

### Key Principles
- Test business logic, not Django/ORM basics
- Use factories for all test data creation
- Maintain test isolation and independence
- Follow consistent naming and organization patterns

## Core Concepts

### Test File Organization

All tests live in the app's `tests/` directory:

```
app/
  company/
    models.py
    services/
      user_service.py
    tests/
      __init__.py
      factories.py
      test_models.py
      test_services/
        __init__.py
        test_user_service.py
```

**Critical Rules:**
- Never create `tests/` directories inside `services/` submodules
- Always place test files in `app/{app_name}/tests/`
- Service tests go in `app/{app_name}/tests/test_services/`
- Test paths mirror source structure under `tests/`

### Base Test Case

All tests inherit from `django_spire.core.tests.test_cases.BaseTestCase`:

```python
from __future__ import annotations
from django_spire.core.tests.test_cases import BaseTestCase

class MyModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_super_user()
        self.company = create_test_company()
```

**BaseTestCase provides:**
- Test client (`self.client`)
- Logged-in superuser (`self.super_user`)
- Temporary MEDIA_ROOT for file uploads

### Hybrid Factory Pattern with **kwargs

Factories belong to the app that owns the model. Use optional FK parameters with auto-creation plus `**kwargs` for flexible field overrides:

```python
# app/company/tests/factories.py
from __future__ import annotations

def create_test_company(**kwargs):
    defaults = {
        'name': 'InMotion Logistics',
        'description': 'Supply chain management solutions',
    }
    defaults.update(kwargs)
    return Company.objects.create(**defaults)
```

```python
# app/company/user/tests/factories.py
from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import User

from app.company.user.models import CompanyUser
from app.company.tests.factories import create_test_company
from django_spire.auth.user.tests.factories import create_user

if TYPE_CHECKING:
    from app.company.models import Company


def create_test_company_user(
    company: Company | None = None,
    user: User | None = None,
    **kwargs
) -> CompanyUser:
    if company is None:
        company = create_test_company()
    if user is None:
        user = create_user('test_user')
    
    # Set sensible defaults that can be overridden via kwargs
    defaults = {
        'company': company,
        'user': user,
        'is_active': True,
        'is_deleted': False,
    }
    defaults.update(kwargs)
    return CompanyUser.objects.create(**defaults)
```

**Factory Rules:**
- Each app has its own `tests/factories.py` file
- Import factories from the app that owns the model
- Use optional FK parameters with auto-creation
- Use `**kwargs` for flexible field overrides
- Set sensible defaults that can be overridden
- Use `create_super_user()` for main test user
- Never create factories for models from other apps
- Always use `from __future__ import annotations` and proper type hints

## Implementation Guide

### Step 1: Create Test File Structure

```bash
# Create test directory structure
mkdir -p app/{app_name}/tests/test_services
touch app/{app_name}/tests/__init__.py
touch app/{app_name}/tests/factories.py
touch app/{app_name}/tests/test_models.py
touch app/{app_name}/tests/test_services/__init__.py
```

### Step 2: Create Test Factories

```python
# app/{app_name}/tests/factories.py
from __future__ import annotations
from app.{app_name}.models import {ModelName}
from django_spire.auth.user.tests.factories import create_super_user, create_user

def create_test_{model_lower}(**kwargs):
    defaults = {
        'name': 'Test {ModelName}',
        'description': 'Test description',
    }
    defaults.update(kwargs)
    
    return {ModelName}.objects.create(**defaults)
```

### Step 3: Write Test Cases

```python
from __future__ import annotations
from django_spire.core.tests.test_cases import BaseTestCase
from app.{app_name}.tests.factories import create_test_{model_lower}

class {ModelName}TestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.{model_lower} = create_test_{model_lower}()
    
    def test_{action}_returns_expected_result(self):
        # Arrange
        # Setup test data if needed
        
        # Act
        result = self.{model_lower}.services.processor.process()
        
        # Assert - verify business logic outcome
        self.assertTrue(result)
        self.assertEqual(expected_value, result.value)
```

### Step 4: What to Test

**DO Test:**
- Business logic outcomes and domain rules
- State changes after method execution
- Edge cases and boundary conditions
- Side effects and downstream actions
- Correct error handling for invalid inputs

**DO NOT Test:**
- Framework/ORM basics (Django saving FKs correctly)
- Attribute assignment verification
- Return value existence unless it's the logic
- Standard CRUD operations

## Examples

### Example 1: Factory Service Test

**DON'T test framework basics:**
```python
def test_create_new_company_user(self):
    company_user = CompanyUser.services.factory.create_or_activate(
        company=self.company, user=self.user
    )
    
    # These test Django, not our logic
    self.assertIsNotNone(company_user)
    self.assertEqual(company_user.company, self.company)
    self.assertEqual(company_user.user, self.user)
```

**DO test business logic:**
```python
def test_create_new_company_user(self):
    initial_count = CompanyUser.objects.count()
    company_user = CompanyUser.services.factory.create_or_activate(
        company=self.company,
        user=self.user
    )
    self.assertEqual(CompanyUser.objects.count(), initial_count + 1)

def test_activate_existing_company_user(self):
    create_test_company_user(
        company=self.company,
        user=self.user,
        is_active=False
    )
    
    company_user = CompanyUser.services.factory.create_or_activate(
        company=self.company,
        user=self.user
    )
    self.assertTrue(company_user.is_active)
    self.assertEqual(CompanyUser.objects.count(), 1)
```

### Example 2: Transformation Service Test

```python
def test_to_wav_creates_file(self):
    self.episode.services.transformation.to_wav()
    original_path = self.episode.audio_path
    new_file = Path(original_path).with_suffix('.wav')
    self.assertTrue(new_file.exists())
    new_file.unlink()
```

### Example 3: Factory with FK Parameters and **kwargs

```python
from __future__ import annotations

from typing import TYPE_CHECKING

from app.podcast.models import Podcast
from app.transcription.models import Transcription
from app.podcast.tests.factories import create_test_podcast
from app.transcription.tests.factories import create_test_transcription
from django_spire.auth.user.tests.factories import create_user

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def create_test_episode(
    podcast: Podcast | None = None,
    transcription: Transcription | None = None,
    user: User | None = None,
    **kwargs
):
    if podcast is None:
        podcast = create_test_podcast()
    if transcription is None:
        transcription = create_test_transcription()
    if user is None:
        user = create_user('test_user')
    
    defaults = {
        'podcast': podcast,
        'transcription': transcription,
        'user': user,
        'name': 'Finding Obvious - DK & Wes go on a journey...',
        'episode_number': 1,
    }
    defaults.update(kwargs)
    
    return Episode.objects.create(**defaults)
```

**Usage in tests:**
```python
def test_with_existing_podcast(self):
    episode = create_test_episode(podcast=self.podcast)

def test_with_auto_created_podcast(self):
    episode = create_test_episode(transcription=self.transcription)

def test_inactive_episode(self):
    episode = create_test_episode(is_active=False)

def test_custom_episode_number(self):
    episode = create_test_episode(episode_number=5, is_featured=True)
```

## Running Tests

### Run tests for a specific app:
```bash
python manage.py test app.explorer
python manage.py test app.podcast.episode
```

### Run specific test file:
```bash
python manage.py test app.podcast.episode.tests.services.test_transformation_service
```

### Run specific test case:
```bash
python manage.py test app.podcast.episode.tests.services.test_transformation_service.EpisodeServiceTransformationTestCase
```

### Run specific test method:
```bash
python manage.py test app.podcast.episode.tests.services.test_transformation_service.EpisodeServiceTransformationTestCase.test_to_wav
```

## Code Review Checklist

When reviewing test files, verify the following:

1. **Base Test Case**: All test classes inherit from `django_spire.core.tests.test_cases.BaseTestCase`
2. **Factory Pattern**: Factories are imported from the correct app directories, not duplicated in test files
3. **Business Logic Focus**: Tests verify business outcomes, not framework basics (ORM saves, attribute assignment)
4. **Test Isolation**: Tests are independent and don't rely on execution order or shared state
5. **Naming Conventions**: Test classes use `{ModuleName}TestCase`, methods use `test_{action}`
6. **Hybrid Factory Pattern**: Factory functions use optional FK parameters with auto-creation plus `**kwargs` for flexible field overrides
7. **File Cleanup**: Tests clean up any created files in teardown or at end of test
8. **Assertion Quality**: Assertions check meaningful outcomes, not just "not None" or equality to inputs
9. **Realistic Data**: Factories use realistic project-based data, not generic placeholders
10. **User Creation**: Tests use `create_super_user()` for main test user, `create_user()` for additional users
11. **No Inline Creation**: Complex object creation uses factories, not inline `objects.create()` calls
12. **Service Testing**: Service tests verify business logic outcomes, not that methods "returned something"
13. **Type Hints**: Factory functions use proper type hints with `from __future__ import annotations` and `TYPE_CHECKING` guards
14. **Sensible Defaults**: Factories set sensible defaults that can be overridden via `**kwargs`

## Related Skills

- [testing](../testing/SKILL.md) - Original testing skill
- [service-layer](../service-layer/SKILL.md) - Service layer patterns for testing
- [python-style](../python_style/SKILL.md) - Coding standards