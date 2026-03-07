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
