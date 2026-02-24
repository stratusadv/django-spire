---
name: button-template
description: How to implement Django Spire buttons in HTML templates.  
---

# Important
- Each button template lives in the django_spire/button/ directory.
- Buttons should be used consistently throughout Django Spire applications.
- Buttons can be customized with different styles and behaviors.
- Django Spire uses Bootstrap icons instead of Font Awesome.

# Buttons
## Folder Structure
```
└── django_spire/
    └── button/
        ├── accent_button.html
        ├── accent_dark_button.html
        ├── accent_outlined_button.html
        ├── danger_button.html
        ├── danger_dark_button.html
        ├── danger_outlined_button.html
        ├── primary_button.html
        ├── primary_dark_button.html
        ├── primary_outlined_button.html
        ├── secondary_button.html
        ├── secondary_dark_button.html
        ├── secondary_outlined_button.html
        ├── success_button.html
        ├── success_dark_button.html
        ├── success_outlined_button.html
        ├── warning_button.html
        ├── warning_dark_button.html
        └── warning_outlined_button.html
```

## Button Types
Django Spire provides various button styles:

### Base Button Structure
All buttons extend the base button template which includes:
- Standard button styling with Bootstrap classes
- Support for href links
- Click event handling with x-data/x-click
- Icon support (using Bootstrap Icons)
- Text content
- Customizable CSS classes

### Available Button Styles
```html
{% include 'django_spire/button/accent_button.html' with button_text='Accent Button' %}
{% include 'django_spire/button/accent_dark_button.html' with button_text='Dark Accent Button' %}
{% include 'django_spire/button/accent_outlined_button.html' with button_text='Outlined Accent Button' %}
{% include 'django_spire/button/danger_button.html' with button_text='Danger Button' %}
{% include 'django_spire/button/danger_dark_button.html' with button_text='Dark Danger Button' %}
{% include 'django_spire/button/danger_outlined_button.html' with button_text='Outlined Danger Button' %}
{% include 'django_spire/button/primary_button.html' with button_text='Primary Button' %}
{% include 'django_spire/button/primary_dark_button.html' with button_text='Dark Primary Button' %}
{% include 'django_spire/button/primary_outlined_button.html' with button_text='Outlined Primary Button' %}
{% include 'django_spire/button/secondary_button.html' with button_text='Secondary Button' %}
{% include 'django_spire/button/secondary_dark_button.html' with button_text='Dark Secondary Button' %}
{% include 'django_spire/button/secondary_outlined_button.html' with button_text='Outlined Secondary Button' %}
{% include 'django_spire/button/success_button.html' with button_text='Success Button' %}
{% include 'django_spire/button/success_dark_button.html' with button_text='Dark Success Button' %}
{% include 'django_spire/button/success_outlined_button.html' with button_text='Outlined Success Button' %}
{% include 'django_spire/button/warning_button.html' with button_text='Warning Button' %}
{% include 'django_spire/button/warning_dark_button.html' with button_text='Dark Warning Button' %}
{% include 'django_spire/button/warning_outlined_button.html' with button_text='Outlined Warning Button' %}
```

## Button Parameters
Each button template accepts the following parameters:
- `button_text`: Text to display on the button
- `button_href`: URL to navigate to when clicked (optional)
- `button_url_params`: Additional URL parameters (optional)
- `x_button_click`: JavaScript click handler (optional)
- `button_modal_href`: Modal view href (optional)
- `button_icon`: Bootstrap icon class (e.g., 'bi bi-plus')
- `button_class`: Additional CSS classes (optional)
- `button_attributes`: Additional HTML attributes (optional)

## Example
### Partner Edit Button
```html
{% url 'partner:form:page' pk=partner.id as form_url %}
{% include 'django_spire/button/primary_button.html' with button_text='Edit' button_icon='bi bi-pencil' button_href=form_url %}
```

## Button Best Practices
1. Use appropriate button colors for their purpose:
   - Primary: Main actions
   - Secondary: Alternative actions
   - Success: Positive actions
   - Warning: Cautionary actions
   - Danger: Destructive actions

2. Always provide meaningful text labels for accessibility

3. Use icons sparingly and only when they enhance usability

4. Maintain consistent button sizes and spacing throughout the application

5. Test buttons with keyboard navigation and screen readers

6. Use Django's `{% url %}` template tag for consistent URL generation


## Review
- Review the skill to ensure it's properly implemented for Django Spire button usage
- Verify that all button types are documented correctly
- Confirm that examples use partner as the main object as requested
- Ensure the documentation covers both basic and advanced button usage patterns