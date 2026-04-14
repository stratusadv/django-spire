---
name: django-glue-forms
description: Django Glue Alpine.js integration for reactive Django forms
---

# Django Glue Forms

## Overview

Django Glue Forms provides seamless Alpine.js integration for Django forms, enabling reactive, two-way data binding between server-side Django forms and client-side JavaScript. It bridges the gap between Django's server-side validation and Alpine.js's reactive UI capabilities.

### Key Features

- **ModelObjectGlue**: Bind Django model instances or form data to Alpine.js reactive objects
- **Automatic Field Generation**: Model fields auto-converted to Alpine.js compatible formats
- **Session Management**: Persistent state across requests with keep-alive functionality
- **Permission Control**: View, change, and delete access levels
- **Form Field Templates**: 20+ pre-built field templates for common Django field types

## Core Concepts

### Two Form Approaches

1. **ModelObjectGlue** - When your form is backed by a model
2. **Frontend Field Initialization** - Collecting data that is not related to a Django Model

**Note**: Both approaches can be used together in the same form.

### Access Levels

```python
from django_glue.access.access import Access

# Permission hierarchy (lowest to highest)
Access.VIEW    # Read-only access
Access.CHANGE  # Read and modify access
Access.DELETE  # Full access including delete
```

### Session Storage

All glue objects are stored in Django session with:
- Unique encoded key (includes request path for isolation)
- Automatic cleanup via middleware
- Keep-alive mechanism to prevent expiration during active use


## Field Templates Available

Located in `django_glue/templates/django_glue/form/field/`:

| Template | Use Case | Django Field Type |
|----------|----------|-------------------|
| `char_field.html` | Text inputs | CharField |
| `email_field.html` | Email inputs | EmailField |
| `password_field.html` | Password inputs | CharField (password) |
| `number_field.html` | Number inputs | IntegerField, FloatField |
| `date_field.html` | Date inputs | DateField |
| `datetime_field.html` | Datetime inputs | DateTimeField |
| `time_field.html` | Time inputs | TimeField |
| `text_field.html` | Textarea inputs | TextField |
| `select_field.html` | Single select dropdowns | ChoiceField, ForeignKey |
| `multi_select_field.html` | Multi-select dropdowns | ManyToManyField |
| `single_checkbox_field.html` | Boolean checkboxes | BooleanField |
| `radio_field.html` | Radio buttons | ChoiceField |
| `search_and_select_field.html` | Searchable selects | ForeignKey |
| `color_field.html` | Color pickers | ColorField |
| `telephone_field.html` | Phone number inputs | CharField (phone) |
| `range_field.html` | Range sliders | FloatField (range) |
| `decimal_field.html` | Decimal inputs | DecimalField |
| `_base_file_field.html` | File upload base | FileField |
| `single_file_field.html` | Single file upload | FileField |
| `multi_file_field.html` | Multiple file upload | FileField (multiple) |
| `_multi_checkbox_field.html` | Multiple checkboxes | MultipleChoiceField |

All field templates extend `base_field.html` which handles:
- Field initialization from session
- Attribute binding (required, disabled, etc.)
- Error display
- Help text tooltips

## How It Works

### 1. Server Initialization

```python
dg.glue_model_object(request, 'company', company_instance, 'change')
```

**What happens:**
1. Creates `ModelObjectGlue` object with model metadata
2. Serializes field definitions (name, type, label, choices, validation rules)
3. Stores in Django session under encoded unique name
4. Sets "keep-alive" flag to maintain session

### 2. Client Initialization

```javascript
company: new ModelObjectGlue('company')
```

**What happens:**
1. Alpine.js component loads
2. `init()` calls `this.company.get()`
3. Makes AJAX request to fetch field data from session
4. Populates reactive object with field definitions and values
5. Fields become available for binding

### 3. Field Binding

```html
{% include 'django_glue/form/field/char_field.html' with glue_model_field='company.name' %}
```

**What happens:**
1. Base template (`base_field.html`) sets up Alpine.js data binding
2. `x-model="value"` binds to `company.name.value`
3. Field attributes (required, disabled, etc.) are applied dynamically
4. Validation errors display automatically
5. Changes sync between Alpine.js and session

### 4. Form Submission

```html
<form method="post">
```

**What happens:**
1. Standard Django form submission
2. Alpine.js values sent as POST data
3. Django form validates against `cleaned_data`
4. Server-side validation errors displayed via `show_form_errors()`
5. On success, redirect or update model

## Real-World Examples

### Your Codebase: Company Form (ModelForm)

**View** (`app/company/views/form_views.py`):
```python
def _form_view(request: WSGIRequest, pk: int):
    company = get_object_or_null_obj(models.Company, pk=pk)
    
    dg.glue_model_object(request, 'company', company, 'view')
    
    if request.method == 'POST':
        form = forms.CompanyForm(request.POST, instance=company)
        
        if form.is_valid():
            company, _ = company.services.save_model_obj(**form.cleaned_data)
            add_form_activity(company, pk, request.user)
            return redirect(return_url)
        
        show_form_errors(request, form)
    else:
        form = forms.CompanyForm(instance=company)
    
    return portal_views.form_view(
        request,
        form=form,
        obj=company,
        template='company/page/form_page.html',
    )
```

**Template** (`templates/company/form/form.html`):
```html
<form method="post" x-data="{
    async init() {
        await this.company.get()
    },
    company: new ModelObjectGlue('company')
}">
    {% csrf_token %}
    
    {% include 'django_glue/form/field/char_field.html' with glue_model_field='company.name' %}
    {% include 'django_glue/form/field/text_field.html' with glue_model_field='company.description' %}
    
    {% include 'django_spire/contrib/form/button/form_submit_button.html' %}
</form>
```

## Frontend Field Initialization

There are two ways to bind form fields with Django Glue:

1. **ModelObjectGlue** - Bind entire model objects (all fields at once)
2. **Manual Field Initialization** - Initialize individual fields directly in Alpine.js

Both approaches use the same field templates. The difference is how you initialize the data in `x-data`.

### Available Glue Field Types

| Field Type | Use Case |
|------------|----------|
| `GlueCharField` | Text inputs |
| `GlueIntegerField` | Integer inputs with min/max/step |
| `GlueDecimalField` | Decimal inputs with step precision |
| `GlueBooleanField` | Boolean checkboxes (Yes/No choices) |
| `GlueDateField` | Date inputs with min/max |

### Common Field Properties

All Glue fields support these properties:

| Property | Type | Description |
|----------|------|-------------|
| `value` | any | Current field value |
| `label` | string | Field label text |
| `choices` | array | Array of `[value, label]` pairs |
| `required` | boolean | Make field required |
| `hidden` | boolean | Hide field from view |
| `read_only` | boolean | Make field read-only |
| `disabled` | boolean | Disable field input |
| `autofocus` | boolean | Auto-focus on field |
| `help_text` | string | Help text tooltip |
| `set_attribute(name, value)` | method | Set custom HTML attribute |
| `remove_attribute(name)` | method | Remove HTML attribute |
| `hide_label()` | method | Hide label visually |
| `show_label()` | method | Show label |

### Manual Field Initialization

Initialize any field type directly in Alpine.js `x-data`:

```html
<form method="post" x-data="{
    async init() {
        // Set initial value
        this.partner_field.value = {{ partner.pk|default_if_none:'null' }}
        
        // Load choices dynamically
        this.partner_field.choices = await this.partners.to_choices()
        
        // Modify field properties
        this.partner_field.label = 'Partner'
        this.partner_field.required = true
        
        // Watch for changes
        this.$watch('partner_field.value', async () => {
            this.agreement_field.choices = await this.get_agreements.call({
                'partner_id': this.partner_field.value
            })
        })
    },
    
    // Initialize standalone fields
    partner_field: new GlueCharField('partner'),
    agreement_field: new GlueCharField('agreement'),
    
    // Supporting objects
    partners: new QuerySetGlue('partners'),
    get_agreements: new FunctionGlue('get_agreements'),
}">
    {% csrf_token %}
    
    <!-- Use glue_field parameter for standalone fields -->
    {% include 'django_glue/form/field/search_and_select_field.html' with glue_field='partner_field' %}
    {% include 'django_glue/form/field/search_and_select_field.html' with glue_field='agreement_field' %}
    
    <button class="btn btn-app-primary">Submit</button>
</form>
```

### Mixing Both Approaches

You can use ModelObjectGlue and standalone fields in the same form:

```html
<form method="post" x-data="{
    async init() {
        // Load model object
        await this.scope_of_work.get()
        
        // Initialize standalone fields
        this.partner_field.choices = await this.partners.to_choices()
    },
    
    // Model-backed fields
    scope_of_work: new ModelObjectGlue('scope_of_work'),
    
    // Standalone fields
    partner_field: new GlueCharField('partner'),
    
    // Supporting objects
    partners: new QuerySetGlue('partners'),
}">
    {% csrf_token %}
    
    <!-- Model field (uses glue_model_field) -->
    {% include 'django_glue/form/field/char_field.html' with glue_model_field='scope_of_work.name' %}
    
    <!-- Standalone field (uses glue_field) -->
    {% include 'django_glue/form/field/search_and_select_field.html' with glue_field='partner_field' %}
    
    <button class="btn btn-app-primary">Submit</button>
</form>
```

**Key Points:**
- Model fields use `glue_model_field='object.field'`
- Standalone fields use `glue_field='field_name'`
- Both use the same field templates
- Initialize standalone fields in `x-data` with `new Glue*Field('name')`

## Advanced Features

### Field Inclusion/Exclusion

```python
# Only include specific fields
dg.glue_model_object(request, 'obj', instance, fields=('name', 'email'))

# Exclude specific fields
dg.glue_model_object(request, 'obj', instance, exclude=('password', 'secret'))

# Include all except some
dg.glue_model_object(request, 'obj', instance, 
                     fields=('__all__',), 
                     exclude=('internal_notes',))
```

### Exposing Model Methods

```python
def my_view(request):
    obj = MyModel.objects.get(pk=1)
    dg.glue_model_object(request, 'obj', obj, methods=('get_full_name',))

# In template
<div x-text="company.get_full_name()"></div>
```



### Exclude Sensitive Fields

Always exclude sensitive data:

```python
dg.glue_model_object(
    request,
    'user',
    user_instance,
    exclude=('password', 'secret_key', 'internal_notes')
)
```

## Code Review Checklist

When reviewing Django Glue Forms code, verify the following:

1. **Glue Initialization**: All views using Glue call `dg.glue_model_object()` before rendering
2. **Name Consistency**: The `unique_name` parameter matches between server and client code
3. **Async Initialization**: Alpine.js components use `async init()` with `.get()` call
4. **CSRF Token**: All forms include `{% csrf_token %}`
5. **Field Parameter**: Using `glue_model_field` for all ModelObjectGlue fields
6. **Access Level**: Appropriate access level ('view', 'change', 'delete') is set
7. **Sensitive Fields**: Password and secret fields are excluded from glue objects
8. **Field Templates**: Appropriate field template is used for each field type
9. **Empty Instance for New Objects**: Regular forms initialize Glue with empty model instance
