---
name: table-template
description: How to implement table templates in Django Spire.  
---

# Important
- Table templates require multiple components to function properly.
- Tables need both header and body sections to work correctly.
- Each table implementation must include the main table container and associated elements.

# Tables
## Folder Structure
```
└── template/
    └── partner/
        └── table/
            ├── table.html
            ├── row.html            
```

## Table Components
Table templates in Django Spire consist of multiple parts:
1. **Main Table Container** (`table.html`): The main wrapper with Alpine.js functionality
2. **Table Row** (`row.html`): Row content for the table

## Basic Table Implementation
`templates/partner/table/table.html`
```html
{% extends 'django_spire/table/base.html' %}

{% block table_header %}
    {% include 'django_spire/table/element/header.html' with sort_key='name' label='Name' %}
    {% include 'django_spire/table/element/header.html' with sort_key='position' label='Position' %}
    {% include 'django_spire/table/element/header.html' with sort_key='type' label='Type' %}
{% endblock %}

{% block table_body %}
	{% for contact in contacts %}
        {% include 'company/contact/table/row.html' %}
    {% endfor %}
{% endblock %}

```

### Table Row
`templates/partner/table/row.html`
```html
{% extends 'django_spire/table/element/row.html' %}

{% block table_cell %}
    <td>{{ contact.full_name }}</td>
    <td>{{ contact.email }}</td>
    <td>{{ contact.get_type_display }}</td>
{% endblock %}
```


## Key Points
- Tables must extend the base table template (`django_spire/table/base.html`)
- Rows should be defined as a separate template
- Each table component should be properly structured with the correct HTML elements
- This modular approach allows for better organization and reusability