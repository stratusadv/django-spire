---
name: ai-intelligence
description: Best practices for AI bots, prompts, and intel in scope_of_work
---

# AI Intelligence

## Overview

AI Intelligence in the scope_of_work module uses LLM-powered bots to automatically generate, process, and review project documentation. This system transforms raw project notes into structured deliverables, labor estimates, and client-ready documentation.

**When to Use:**
- Generating scope of work overviews from meeting notes
- Creating deliverable descriptions from project requirements
- Estimating labor hours for software development tasks
- Generating hosting and additional expense line items
- Reviewing and refining AI-generated content

**Key Principles:**
- **Typed Output**: All bot results use structured intel classes for type safety
- **Composable Prompts**: Reusable prompt functions ensure consistency
- **Clear Personas**: Bot roles define LLM behavior and expertise
- **Guided Generation**: Detailed guidelines prevent common mistakes
- **Workflow Chaining**: Multiple bots work together for complex tasks

## Core Concepts

### Bot Architecture

Bots are the primary interface for LLM interactions. Each bot defines a persona, task, and output structure.

**Three Critical Components:**

1. **`role`** - Defines the bot's persona and expertise (50-150 words)
2. **`guidelines`** - Structured instructions using `Prompt()` class
3. **`intel_class`** - Typed output structure that enforces consistency

### Prompt Formatting

The `Prompt()` class structures data for LLM consumption:

```python
prompt = (
    Prompt()
    .heading('Scope of Work')
    .sub_heading('Project Notes')
    .text(scope_of_work.notes)
    .line_break()
    .sub_heading('Deliverables')
    .list(['Deliverable 1', 'Deliverable 2'])
)
```

### Intel Classes

Intel classes define structured output from LLM responses:

```python
class DeliverableIntel(BaseIntel):
    name: str
    summary: str
    features: list[str]
    life_cylce: ScopeOfWorkDeliverableLifeCycleChoices
    labour_items: LabourLineItemsIntel | None
```

**Key Methods:**
- `to_prompt()` - Convert intel back to prompt format
- `to_string()` / `__str__()` - String representation

## Bot Implementation

### Bot Structure

Every bot follows this pattern:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

from dandy import Bot, Prompt

from app.partner.scope_of_work.deliverable.intelligence import intel

if TYPE_CHECKING:
    from app.partner.scope_of_work.models import ScopeOfWork


class DeliverableBot(Bot):
    role = 'Scope of Work Architect: A detail-oriented and pragmatic project strategist...'
    task = 'Define clear, concise deliverable that fully highlights features and items being delivered.'
    guidelines = (
        Prompt()
        .list([
            'Name should be in the format "App Name: Description".',
            'The summary should be 3 - 4 sentences that focuses on benefits.',
            'Features should be 12 words or less.',
            'Avoid technical jargon.',
        ])
        .text('Life Cycle Choices')
        .list([
            'Wireframe - Only select if specifically mentioned.',
            'Alpha - Most of the time this is the option.',
            'Beta - Select if we are improving what we have already built.',
        ])
    )
    intel_class = intel.DeliverableIntel

    def process(self, description: str, scope_of_work: ScopeOfWork) -> intel.DeliverableIntel:
        deliverables = scope_of_work.deliverables.active()

        deliverable_description = ''
        for deliverable in deliverables:
            deliverable_description += f'{deliverable.name}: {deliverable.description}\n'

        return self.llm.prompt_to_intel(
            Prompt()
            .heading('New Deliverable Description')
            .text(description)
            .heading('Scope Of Work')
            .text(f'Name: {scope_of_work.name}, Notes: {scope_of_work.notes}')
            .heading('Existing Deliverables')
            .text(deliverable_description)
        )
```

**Guidelines Definition:**

- **Define inline** when guidelines are used only by this bot
- **Use prompt functions** only when guidelines are reused in multiple places (e.g., multiple bots share the same guidelines)

### Role Definition Best Practices

**Role Length:** 50-150 words describing expertise and communication style

**Effective Roles:**
```python
# Client-Focused
role = 'Client-Friendly Project Translator: A clear-communicating, business-savvy project specialist who translates technical software development goals into simple, engaging, and outcome-focused language that resonates with non-technical stakeholders.'

# Technical Expert
role = 'Scope of Work Architect: A detail-oriented and pragmatic project strategist with expertise in translating client needs into clear, impactful deliverables that emphasize key features, measurable business value, and tangible improvements over legacy processes.'

# Estimator
role = 'Estimator - A project manager with a knowledge of software development. Equipped with the rare ability to distill complex tasks into clear, confident, and unambiguous descriptions.'
```

**Role Guidelines:**
- Start with a title that defines the expertise area
- Include communication style (clear, confident, business-savvy)
- Specify the transformation or output expected
- Mention the target audience when relevant

### Guidelines Composition

Guidelines use `Prompt()` for structured instruction delivery:

```python
guidelines = (
    Prompt()
    .list([
        'The user will provide you with instructions or meeting notes where they are talking about a scope of work for a software project.',
        'The name should be no longer than 6 words and be relatable to the client.',
        'The description should be 2 clear paragraphs that focuses on the client's outcome—not technical details.',
        'Keep each paragraph between 3-5 sentences—concise, warm, and confident.',
    ])
    .heading('Life Cycle Choices')
    .list([
        'Wireframe - Only select if it specifically mentioned.',
        'Prototype - Only select prototype if it specifically mentioned.',
        'Alpha - Most of the time this is the option. Clients need a working version.',
        'Beta - Select if we are improving what we have already built.',
        'Stable - Only select if specifically mentioned. This is the final stage.',
    ])
)
```

**Guidelines Best Practices:**
- Use `.list()` for multiple related instructions
- Use `.heading()` and `.sub_heading()` for organization
- Include edge cases and common mistakes
- Reference reusable prompt functions when possible
- Add conditional logic for special cases (e.g., Django Spire Enterprise features)

### LLM Settings

When working with LLM configurations:

**Temperature Settings:**
- **Creative tasks** (overviews, descriptions): 0.7-0.8
- **Structured tasks** (line items, estimates): 0.3-0.5
- **Review tasks** (refinement, validation): 0.2-0.4

**Model Selection:**
- Use the default model from the `dandy` library configuration
- Ensure consistent model usage across related bots for predictable results

**Processing Methods:**
- `self.llm.prompt_to_intel(prompt)` - Standard intel extraction
- `self.llm.prompt_to_intel(prompt, temperature=0.5)` - Override temperature when needed

## Prompt Patterns

### Role Prompts

Separate functions for role definitions enable reuse:

```python
def deliverable_role_prompt():
    return 'Scope of Work Architect: A detail-oriented and pragmatic project strategist with expertise in translating client needs into clear, impactful deliverables that emphasize key features, measurable business value, and tangible improvements over legacy processes.'
```

**Usage:**
```python
class DeliverableBot(Bot):
    role = prompts.deliverable_role_prompt()
```

### Guidelines Prompts

Reusable instruction sets maintain consistency:

```python
def deliverable_guidelines_prompt():
    return (
        Prompt()
        .list([
            'Name should be in the format "App Name: Description". App name is 1-3 words and is main entity or feature. Description is 4 words or less.',
            'The summary should be 3 - 4 sentences that focuses on what the client will receive and the benefits.',
            'A feature is a tangible benefit or improvement that the client will receive from the deliverable.',
            'List the features in bullet points.',
            'Features should be 12 words or less.',
            'Avoid technical jargon.',
        ])
        .text('Life Cycle Choices')
        .list([
            'Wireframe - Only select if it specifically mentioned.',
            'Prototype - Only select prototype if it specifically mentioned.',
            'Alpha - Most of the time this is the option.',
            'Beta - Select if we are improving what we have already built.',
            'Stable - Only select if specifically mentioned.',
        ])
    )
```

### Data Prompts

Format model data for LLM consumption:

```python
def deliverable_prompt(deliverable: ScopeOfWorkDeliverable, show_line_items: bool = True):
    prompt = Prompt()

    prompt.sub_heading(deliverable.name)
    prompt.line_break()
    prompt.text(deliverable.description)
    prompt.line_break()

    line_items = deliverable.line_items.active()

    if show_line_items and line_items.exists():
        prompt.sub_heading('Line Items')
        prompt.line_break()

        for line_item in line_items:
            prompt.prompt(line_item_prompt(line_item))

    return prompt
```

### Composite Prompts

Combine multiple sources for context:

```python
def scope_of_work_prompt(scope_of_work: ScopeOfWork):
    prompt = Prompt()

    prompt.heading('Scope of Work')
    prompt.line_break()
    prompt.sub_heading('Project Notes')
    prompt.line_break()
    prompt.text(scope_of_work.notes)

    if scope_of_work.overview:
        prompt.line_break()
        prompt.sub_heading('Project Overview')
        prompt.text(scope_of_work.overview)

    deliverables = scope_of_work.deliverables.active()

    if deliverables.exists():
        prompt.line_break()
        prompt.heading('Deliverables')
        for deliverable in deliverables:
            prompt.line_break()
            prompt.prompt(deliverable_prompt(deliverable))

    return prompt
```

**Composite Prompt Guidelines:**
- Use headings to separate different data sources
- Include all relevant context the LLM needs
- Maintain consistent formatting across sections
- Use `line_break()` between major sections

## Intel Design

### Base Intel Structure

All intel classes inherit from `BaseIntel`:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

from dandy import BaseIntel, BaseListIntel

from app.partner.scope_of_work.line_item.choices import ScopeOfWorkLineItemTypeChoices
from app.partner.scope_of_work.line_item.enums import ScopeOfWorkSkillEnum
from app.partner.scope_of_work.line_item.models import ScopeOfWorkLineItem

if TYPE_CHECKING:
    from app.partner.scope_of_work.deliverable.models import ScopeOfWorkDeliverable
    from app.partner.scope_of_work.models import ScopeOfWork


class LabourLineItemIntel(BaseIntel):
    name: str
    description: str
    quantity: float
    skill_level: ScopeOfWorkSkillEnum

    @property
    def skill_level_choice(self) -> str:
        return self.skill_level.to_choice()

    @property
    def skill_level_rate_choice(self) -> Decimal:
        return self.skill_level.to_rate_choice()

    def to_model_obj(
            self,
            scope_of_work: ScopeOfWork,
            deliverable: ScopeOfWorkDeliverable
    ) -> ScopeOfWorkLineItem:
        return ScopeOfWorkLineItem(
            scope_of_work=scope_of_work,
            deliverable=deliverable,
            type=ScopeOfWorkLineItemTypeChoices.LABOUR,
            name=self.name,
            description=self.description,
            quantity=self.quantity,
            skill_level=self.skill_level_choice,
        )
```

### List Intel for Collections

Use `BaseListIntel` for collections:

```python
class LabourLineItemsIntel(BaseListIntel[LabourLineItemIntel]):
    labour_items: list[LabourLineItemIntel]

    def to_model_objs(
            self,
            scope_of_work: ScopeOfWork,
            deliverable: ScopeOfWorkDeliverable
    ):
        return [l.to_model_obj(scope_of_work, deliverable) for l in self.labour_items]
```

### Nested Intel Structures

Intel can contain other intel objects:

```python
class DeliverableIntel(BaseIntel):
    name: str
    summary: str
    features: list[str]
    life_cylce: ScopeOfWorkDeliverableLifeCycleChoices

    labour_items: LabourLineItemsIntel | None

    def format_description(self) -> str:
        return f'{self.summary}\n {self.format_features()}'

    def format_features(self) -> str:
        features = ''
        for feature in self.features:
            features += f'- {feature}\n'
        return features

    def to_prompt(self):
        return (
            Prompt()
            .heading(self.name)
            .text(self.summary)
            .list(self.features)
        )

    def to_string(self) -> str:
        return f'{self.name} \n {self.format_description()} \n {self.format_features()}'

    def to_model_obj(self, scope_of_work: ScopeOfWork) -> ScopeOfWorkDeliverable:
        return ScopeOfWorkDeliverable(
            scope_of_work=scope_of_work,
            name=self.name,
            description=self.format_description(),
            life_cycle=self.life_cylce
        )
```

### Conversion Methods

**`to_prompt()` - Convert to Prompt:**

```python
def to_prompt(self) -> Prompt:
    return (
        Prompt()
        .sub_heading('Title')
        .text(self.title)
        .line_break()
        .sub_heading('Overview')
        .text(self.overview)
        .line_break()
        .sub_heading('Discussed Items')
        .list([d for d in self.discussed_items])
        .line_break()
    )
```

**`to_string()` / `__str__()` - String Representation:**

```python
def __str__(self) -> str:
    return self.html_content
```

**`to_model_obj()` - Convert to Django Model:**

```python
def to_model_obj(self, scope_of_work: ScopeOfWork) -> ScopeOfWorkDeliverable:
    return ScopeOfWorkDeliverable(
        scope_of_work=scope_of_work,
        name=self.name,
        description=self.format_description(),
        life_cycle=self.life_cylce
    )
```

## Workflow Patterns

### Single Bot Processing

Simple one-step processing:

```python
class ScopeOfWorkOverviewBot(Bot):
    role = 'Client-Friendly Project Translator: A clear-communicating, business-savvy project specialist...'
    task = 'Write an overview for a software scope of work.'
    guidelines = Prompt().list([...])
    intel_class = intel.ScopeOfWorkOverviewIntel

    def process(self, description: str) -> intel.ScopeOfWorkOverviewIntel:
        return self.llm.prompt_to_intel(prompt=description)
```

**Usage:**
```python
overview_intel = ScopeOfWorkOverviewBot().process(project_notes)
```

### Multi-Bot Chain (Deliverables)

Complex workflows use multiple bots in sequence:

```python
class BulkDeliverablesBot(Bot):
    role = prompts.deliverable_role_prompt()
    task = 'Return a list of formatted deliverables.'
    guidelines = (
        Prompt()
        .heading('Bulk Guidelines')
        .list([
            'The user will give you a list of deliverables to create along with the reference text.',
            'Use the reference text to find information relating to each deliverable.',
            'Keep the deliverables in order.',
            'The deliverable features should not overlap.',
        ])
        .heading('Individual Deliverable Guidelines')
        .prompt(prompts.deliverable_guidelines_prompt())
    )
    intel_class = DeliverablesIntel

    def process(self, deliverables: FoundIntel, instructions: Prompt) -> DeliverablesIntel:
        deliverables_intel = []
        for deliverable in deliverables.items:
            deliverables_intel.append(SingleDeliverablesBot().process(
                deliverable=deliverable,
                instructions=str(instructions)
            ))

        return intel.DeliverablesIntel(deliverables=deliverables_intel)
```

**Complete Workflow:**
```python
# Step 1: Extract deliverable names
finder_intel = FinderBot().process(user_prompt, project_context)

# Step 2: Create bulk deliverables
bulk_intel = BulkDeliverablesBot().process(finder_intel, scope_prompt)

# Step 3: Add labor estimates
for deliverable in bulk_intel.deliverables:
    deliverable.labour_items = DeliverableLaborLineItemBot().process(deliverable)

# Step 4: Review and refine
final_intel = DeliverablesReviewBot().process(bulk_intel)

# Step 5: Convert to models
deliverable_objs = final_intel.to_model_objs(scope_of_work)
```

### Review Workflows

Review bots refine AI-generated content:

```python
class DeliverablesReviewBot(Bot):
    role = prompts.deliverable_role_prompt()
    task = 'Review the scope of work deliverables.'
    guidelines = (
        Prompt()
        .heading('Review Guidelines')
        .list([
            'Do not make major changes to the deliverables.',
            'The main goal is to improve how the deliverables are read together.',
            'The deliverables should not repeat information between on another.',
            'The descriptions should flow from one deliverable to the next without referencing each other.',
        ])
        .heading('Deliverable Guidelines')
        .prompt(prompts.deliverable_guidelines_prompt())
    )
    intel_class = DeliverablesIntel

    def process(self, deliverables: DeliverablesIntel) -> DeliverablesIntel:
        prompt = (
            Prompt()
            .heading('Deliverables')
            .prompt(deliverables.to_prompt())
        )

        return self.llm.prompt_to_intel(prompt)
```

### Factory Workflows

Bots that create related objects:

```python
class DeliverableLaborLineItemBot(Bot):
    role = 'Expert Software Project Manager'
    task = 'You are breaking down a deliverable and estimating labour hours.'
    guidelines = (
        Prompt()
        .heading('For each deliverable')
        .list([
            'Labour items: Tasks needed to complete it',
        ])
        .line_break()
        .heading('For each labour item')
        .list([
            'Name: Use "Software Architecture", "Logic & Programming", "User Interface", "Testing & QA", or "Documentation"',
            'Description: Brief task description',
            'Quantity: Estimated hours',
            'Skill level: Junior, Intermediate, Senior, or Intelligence',
        ])
    )
    intel_class = LabourLineItemsIntel

    def process(self, deliverable_intel: DeliverableIntel) -> DeliverableIntel:
        labour_line_items_intel = self.llm.prompt_to_intel(
            prompt=(
                Prompt()
                .heading('Deliverable')
                .line_break()
                .sub_heading('Name')
                .text(deliverable_intel.name)
                .line_break()
                .sub_heading('Description')
                .text(deliverable_intel.description)
            )
        )

        deliverable_intel.labour_items = labour_line_items_intel

        return deliverable_intel
```

## Examples

### Complete Bot Implementation

**DON'T: Generic role and minimal guidelines**

```python
class BadDeliverableBot(Bot):
    role = 'Project Bot'
    task = 'Make deliverables.'
    guidelines = Prompt().list(['Do a good job.'])
    intel_class = intel.DeliverableIntel

    def process(self, description: str):
        return self.llm.prompt_to_intel(description)
```

**DO: Specific role and comprehensive guidelines**

```python
from __future__ import annotations
from typing import TYPE_CHECKING

from dandy import Bot, Prompt

from app.partner.scope_of_work.deliverable.intelligence import intel, prompts

if TYPE_CHECKING:
    from app.partner.scope_of_work.models import ScopeOfWork


class DeliverableBot(Bot):
    role = prompts.deliverable_role_prompt()
    task = 'Define clear, concise deliverable that fully highlights features and items being delivered.'
    guidelines = prompts.deliverable_guidelines_prompt()
    intel_class = intel.DeliverableIntel

    def process(self, description: str, scope_of_work: ScopeOfWork) -> intel.DeliverableIntel:
        deliverables = scope_of_work.deliverables.active()

        deliverable_description = ''
        for deliverable in deliverables:
            deliverable_description += f'{deliverable.name}: {deliverable.description}\n'

        return self.llm.prompt_to_intel(
            Prompt()
            .heading('New Deliverable Description')
            .text(description)
            .heading('Scope Of Work')
            .text(f'Name: {scope_of_work.name}, Notes: {scope_of_work.notes}')
            .heading('Existing Deliverables')
            .text(deliverable_description)
        )
```

### Prompt Composition Example

**DON'T: Inline prompt construction**

```python
def process(self, description: str, scope_of_work: ScopeOfWork):
    prompt = Prompt()
    prompt.heading('New Deliverable Description')
    prompt.text(description)
    prompt.heading('Scope Of Work')
    prompt.text(f'Name: {scope_of_work.name}')
    # ... more inline construction
    return self.llm.prompt_to_intel(prompt)
```

**DO: Reusable prompt functions**

```python
# prompts.py
def deliverable_prompt(deliverable: ScopeOfWorkDeliverable, show_line_items: bool = True):
    prompt = Prompt()
    prompt.sub_heading(deliverable.name)
    prompt.text(deliverable.description)

    if show_line_items:
        line_items = deliverable.line_items.active()
        if line_items.exists():
            prompt.sub_heading('Line Items')
            for line_item in line_items:
                prompt.prompt(line_item_prompt(line_item))

    return prompt


# bots.py
def process(self, description: str, scope_of_work: ScopeOfWork):
    prompt = (
        Prompt()
        .heading('New Deliverable Description')
        .text(description)
        .heading('Scope Of Work')
        .text(f'Name: {scope_of_work.name}, Notes: {scope_of_work.notes}')
        .heading('Existing Deliverables')
        .text(self._format_existing_deliverables(scope_of_work))
    )
    return self.llm.prompt_to_intel(prompt)
```

### Intel Conversion Workflow

**DON'T: Manual model creation**

```python
def save_deliverables(intel: DeliverablesIntel, scope_of_work: ScopeOfWork):
    for deliverable_data in intel.deliverables:
        deliverable = ScopeOfWorkDeliverable(
            scope_of_work=scope_of_work,
            name=deliverable_data.name,
            description=f'{deliverable_data.summary}\n{deliverable_data.format_features()}',
            life_cycle=deliverable_data.life_cylce
        )
        deliverable.save()
```

**DO: Use built-in conversion methods**

```python
def save_deliverables(intel: DeliverablesIntel, scope_of_work: ScopeOfWork):
    deliverable_objs = intel.to_model_objs(scope_of_work)
    for obj in deliverable_objs:
        obj.save()
```

### Complete Workflow Example

**Real-world deliverable creation workflow:**

```python
from __future__ import annotations
from typing import TYPE_CHECKING

from dandy import Prompt

from app.ai.intelligence.bots import FinderBot
from app.partner.scope_of_work.deliverable.intelligence.bots import (
    BulkDeliverablesBot,
    DeliverablesReviewBot,
    DeliverableLaborLineItemBot,
)
from app.partner.scope_of_work.intelligence.prompts import scope_of_work_prompt

if TYPE_CHECKING:
    from app.partner.scope_of_work.models import ScopeOfWork


def create_deliverables_from_notes(
    user_request: str,
    project_context: str,
    scope_of_work: ScopeOfWork
) -> list[ScopeOfWorkDeliverable]:
    """
    Complete workflow: Extract deliverables, create descriptions, add estimates, review.
    """
    # Step 1: Find deliverable names in project notes
    finder_intel = FinderBot().process(
        user_prompt=user_request,
        reference_text=project_context
    )

    # Step 2: Create bulk deliverables with descriptions
    scope_prompt = scope_of_work_prompt(scope_of_work)
    bulk_intel = BulkDeliverablesBot().process(
        deliverables=finder_intel,
        instructions=scope_prompt
    )

    # Step 3: Add labor estimates to each deliverable
    for deliverable in bulk_intel.deliverables:
        deliverable.labour_items = DeliverableLaborLineItemBot().process(deliverable)

    # Step 4: Review and refine for consistency
    final_intel = DeliverablesReviewBot().process(bulk_intel)

    # Step 5: Convert to Django models
    return final_intel.to_model_objs(scope_of_work)
```

## Code Review Checklist

When reviewing AI intelligence code, verify the following:

1. **Role Specificity**: Role definition is 50-150 words with clear expertise and communication style
2. **Guidelines Completeness**: Guidelines cover edge cases, common mistakes, and output formatting
3. **Prompt Structure**: Prompts use headings, subheadings, and lists for clear organization
4. **Intel Type Safety**: All intel fields have proper type hints
5. **Conversion Methods**: Intel classes implement `to_prompt()`, `to_string()`, and `to_model_obj()` as needed
6. **Reusability**: Role and guidelines prompts use separate functions for reuse
7. **Context Inclusion**: Bots include all relevant context in their prompts
8. **Error Handling**: Consider what happens if LLM returns unexpected results
9. **Workflow Efficiency**: Multi-bot chains minimize redundant LLM calls
10. **Temperature Settings**: Appropriate temperature used for the task type
11. **List Intel Usage**: Collections use `BaseListIntel` with typed generics
12. **Nested Intel**: Complex objects properly nest related intel classes
13. **Model Conversion**: `to_model_obj()` methods handle all required fields
14. **Prompt Formatting**: `Prompt()` class methods used consistently
15. **Documentation**: Complex workflows include inline explanations

## Related Skills

- **[skill-writing](../skill-writing/SKILL.md)** - Best practices for writing and updating skill files
- **[django-models](../models/SKILL.md)** - Django model patterns and conventions
- **[service-layer](../service-layer/SKILL.md)** - Service layer architecture and patterns
- **[python-style](../python-style/SKILL.md)** - Python coding standards and best practices
