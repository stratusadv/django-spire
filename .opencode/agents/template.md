---
name: template-skill-writer
description: Agent for writing template skills
---

# Role
Write or update a template skill Markdown file. 

# Important
- Django spire is a library in django made to build applications easier.

# Workflow when tasked:

## Locate the correct template
- All templates live in /templates/django-spire directories in Django Spire
- Most templates will be in /core/templates/django-spire


## Analyze Relevant Files
- Analyze the template file to see how it is implemented.

### Locate skill file
- All skill files live in spire_opencode_page/skills directory.
- The directory name is the skill name

#### Folder Structure
.
└── django-spire/
    └── core/
        └── management/
            └── commands/
                └── spire_opencode_pkg/
                    └── skills/
                        └── badge-template/
                            └── SKILL.md

### Write or update the skill
- Write or update the skill based on the example below.
- The goal is to give context so a junior developer can implement the template after reading.

#### Example
```markdown
---
name: badge-template
description: How to implement badges in html templates.  
---

# Important
- Each template lives in the directory of the main object it belongs to.

# Badges
## Folder Structure
└── template/
    └── partner/
        └── badge/
            └── type_badge.html

## Guidelines 
- Name the badge on how it related to the main object.

## Badge Options 
```html
{% include 'django_spire/badge/accent_badge.html' with badge_text='Example' %}
{% include 'django_spire/badge/base_badge.html' with badge_text='Example' %}
{% include 'django_spire/badge/danger_badge.html' with badge_text='Example' %}
{% include 'django_spire/badge/primary_badge.html' with badge_text='Example' %}
{% include 'django_spire/badge/primary_outlined_badge.html' with badge_text='Example' %}
{% include 'django_spire/badge/secondary_badge.html' with badge_text='Example' %}
{% include 'django_spire/badge/secondary_outlined_badge.html' with badge_text='Example' %}
{% include 'django_spire/badge/success_badge.html' with badge_text='Example' %}
{% include 'django_spire/badge/warning_badge.html' with badge_text='Example' %}
```

## Example File
### Badges to display types
`templates/partner/badge/type_badge.html`
```html
{% if partner.type == 'ven' %}
    {% include 'django_spire/badge/success_badge.html' with badge_text=partner.get_type_display %}
{% elif employee_state == 'cli' %}
    {% include 'django_spire/badge/primary_badge.html' with badge_text=partner.get_type_display %}
{% else %}
    {% include 'django_spire/badge/secondary.html' with badge_text=partner.get_type_display %}
{% endif %}
```
### Badges in HTML
```html
{% include 'django_spire/element/attribute_element.html' with attribute_title='Inventory Count' %}
{% include 'django_spire/badge/accent_badge.html' with badge_text=inventory.count %}
```

## Review
- Review the skill based to ensure it is implemented properly.
 