---
name: skill-writing
description: Best practices for writing and updating skills
---

# Skill Writing Best Practices

## Overview

This skill provides guidelines for creating and maintaining skill files. Skills are the primary way we document conventions, patterns, and best practices for consistent development across the project.

### Key Principles
- **Single Source of Truth**: Each concept should be documented in one place
- **Clear Hierarchy**: Use consistent heading structure across all skills
- **Code Examples**: Every pattern should have working code examples
- **Do's and Don'ts**: Show both correct and incorrect usage
- **Actionable Checklists**: Include code review sections for verification

## Core Structure

### Skill File Format

Every skill file must follow this structure:

```markdown
---
name: {skill-name}
description: {clear, concise description in 10-15 words}
---

# {Skill Title}

## Overview
- Purpose and scope
- When to use this skill
- Key principles

## Core Concepts
- Fundamental patterns
- Important rules
- Common pitfalls

## Implementation Guide
- Step-by-step instructions
- Code examples
- Best practices

## Examples
- Complete working examples
- Do's and Don'ts comparisons
- Real-world use cases

## Code Review Checklist
- Numbered list for code review actions

## Related Skills
- Links to complementary skills
```

### YAML Front Matter

```yaml
---
name: {kebab-case-skill-name}
description: {Action-oriented description}
---
```

**Rules:**
- `name`: Use kebab-case, match directory name
- `description`: Concise description (approximately 10-15 words)

### Heading Hierarchy

``` markdown
# Skill Title (H1)
## Section (H2)
### Subsection (H3)
#### Code Block/Example (H4 - optional)
```

**Rules:**
- Always start with H1 for skill title
- Use H2 for major sections
- Use H3 for subsections within major sections
- Never skip heading levels

## Content Guidelines

### Writing Clear Sections

**Overview Section:**
- 1-2 sentences explaining the skill's purpose
- 3-5 key principles

**Core Concepts Section:**
- Define fundamental patterns
- List critical rules (use bold for emphasis)
- Highlight common mistakes to avoid

**Implementation Guide:**
- Numbered steps for processes
- Code blocks for each step
- Include both simple and complex examples

**Examples Section:**
- Show "DON'T" patterns first (what to avoid)
- Show "DO" patterns second (correct approach)
- Use realistic, project-based data

### Code Examples

**Format:**
```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.example.models import Example

class ExampleService(BaseDjangoModelService['Example']):
    obj: Example
    
    def process(self) -> Example:
        self.obj.status = 'processed'
        return self.save_model_obj()
```

**Rules:**
- Always include `from __future__ import annotations`
- Use `TYPE_CHECKING` guards for imports
- Show complete, working code
- Include type hints
- No comments inside code blocks (code should be self-explanatory)
- Follow [python-style](../python-style/SKILL.md) guidelines - code must be self-documenting

### Do's and Don'ts Pattern

**DON'T Example:**
```python
# ❌ DON'T: Direct attribute setting and save
company_user.is_active = True
company_user.save()
```

**DO Example:**
```python
# ✅ DO: Using save_model_obj with field names
obj, is_created = company_user.services.save_model_obj(is_active=True)
return obj
```

**When to Use:**

**Both DO and DON'T (preferred for):**
- Pattern shifts where the old way looks correct but isn't
- Subtle mistakes that are easy to make
- New team conventions that need reinforcement
- Complex workflows with multiple failure points

**DO Only (acceptable for):**
- Obvious anti-patterns (e.g., "don't use `eval()`")
- Simple formatting rules (e.g., "use kebab-case")
- When the correct pattern is self-explanatory

**Rules:**
- Use emoji indicators (❌/✅) for visual clarity
- Include brief explanation before code
- Show the problem, then the solution
- Keep DON'T examples concise - focus on the mistake, not the full context

## Code Review Checklist

Every skill must include a Code Review section with numbered actions:

```markdown
## Code Review Checklist

When reviewing {domain} code, verify the following:

1. **Rule Name**: Description of what to check
2. **Rule Name**: Description of what to check
3. **Rule Name**: Description of what to check
```

**Creating Review Items:**
- Start with action verb (Verify, Check, Ensure, Confirm)
- Make each item specific and testable
- Cover the most common mistakes


## Content Quality Rules

### Avoid Duplication

Do not repeat information inside of a skill. Keep them concise.

**Guidelines:**
- One concept per section
- Cross-reference instead of repeating
- Check other skills before creating new content


## Skill File Review Checklist

When reviewing skill files, verify the following:

1. **YAML Front Matter**: Name and description are present and correctly formatted
2. **Heading Structure**: Follows H1 → H2 → H3 hierarchy without skipping levels
3. **No Duplication**: Each concept appears in only one location
4. **Code Examples**: All patterns include complete, working code examples
5. **Do's and Don'ts**: Both incorrect and correct patterns are shown when relevant.
6. **Code Review Section**: Includes numbered checklist with approximately 8-15 items
7. **Related Skills**: Links to complementary skills are provided
8. **Realistic Data**: Examples use project-based realistic data
9. **Actionable Checklists**: Review items are specific and testable
