---
name: container-template
description: How to implement container templates in Django Spire.  
---

# Important
- Container templates provide consistent layout structures for pages in Django Spire.
- Containers are used when we are displaying a main object and want to have it on the first layer.
- Containers can be extended and customized with blocks for flexibility.

# Container Templates

## Folder Structure
```
└── partner/
    └── conatiner/
        └── detail_conatainer.html           
```

## Container Structure
The core container.html template provides:
- A responsive row structure with appropriate Bootstrap classes
- Title section with customizable heading
- Button section for action buttons
- Content area for main page content
- Flexible block extensions for customization

## Container Blocks
- `container_title`: Main page title
- `container_button`: Action buttons (use Django Spire buttons here)
- `container_filter_section`: Optional filter controls
- `container_content`: Main content area
- `container_outer_class`: Additional CSS classes for outer container
- `container_title_class`: Additional CSS classes for title
- `container_class`: Additional CSS classes for content container
- `container_content_class`: Additional CSS classes for content area

## Example Usage
### Basic Container Implementation
```html
{% extends 'django_spire/container/container.html' %}

{% block container_title %}User Management{% endblock %}

{% block container_button %}
    {% include 'django_spire/button/primary_button.html' with button_text='Add User' button_url='/users/add/' %}
{% endblock %}

{% block container_content %}
    <p>This is the user management page content.</p>
{% endblock %}
```

## Best Practices
1. Always extend the base container template
2. Use `container_title` for page headings
3. Place action buttons in `container_button` block
5. Put main content in `container_content` block
6. Customize classes using the available block extensions
7. Combine container templates with Django Spire components for consistency
