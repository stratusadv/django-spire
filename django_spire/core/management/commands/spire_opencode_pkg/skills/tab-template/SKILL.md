---
name: tab-template
description: How to implement tab templates in Django Spire.  
---

# Important
- Tab sections must be extended with specific templates, not just included.
- Each tab section should have its own dedicated template file.
- This ensures proper inheritance and content organization.

# Tabs
## Folder Structure
```
└── template/
    └── partner/
        └── tab/
            ├── tabs.html
            ├── contact_tab.html
            ├── work_tab.html
            └── notes_tab.html
```

## Tab Implementation
For each tab section, you must create a dedicated template that extends the Django Spire tab section element:

### Main Tab Container
`templates/partner/tab/tabs.html`
```html
{% extends 'django_spire/tab/tab.html' %}

{% block tab_triggers %}
    {% include 'django_spire/tab/element/tab_trigger_element.html' with trigger_title='Contacts' %}
    {% include 'django_spire/tab/element/tab_trigger_element.html' with trigger_title='Work' %}
    {% include 'django_spire/tab/element/tab_trigger_element.html' with trigger_title='Notes' %}
{% endblock %}

{% block tab_sections %}
    {% include 'partner/tab/contact_tab.html' %}
    {% include 'partner/tab/work_tab.html' %}
    {% include 'partner/tab/notes_tab.html' %}
{% endblock %}
```

### Partner Tab Sections
Each tab section should extend the base tab section element:

`templates/partner/tab/contact_tab.html`
```html
{% extends 'django_spire/tab/element/tab_section_element.html' %}

{% block tab_section_content %}
    <h3>Partner Contacts</h3>
    <p>Contact information would go here.</p>
{% endblock %}
```

`templates/partner/tab/work_tab.html`
```html
{% extends 'django_spire/tab/element/tab_section_element.html' %}

{% block tab_section_content %}
    <h3>Partner Work Information</h3>
    <p>Work details would go here.</p>
{% endblock %}
```

`templates/partner/tab/notes_tab.html`
```html
{% extends 'django_spire/tab/element/tab_section_element.html' %}

{% block tab_section_content %}
    <h3>Partner Notes</h3>
    <p>Notes and comments would go here.</p>
{% endblock %}
```

## Key Points
- Tab sections must extend `django_spire/tab/element/tab_section_element.html`
- Each tab section should have its own dedicated template file
- This allows for proper content organization and inheritance
- The main tab container includes the specific tab section templates
