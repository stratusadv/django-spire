---
name: form-views
description: Examples on how we build our form views. 
---

# Guidelines
- Use the examples as the base implementation. 
- You will have to refactor out friend and ensure the custom paths are correct.
- All django spire paths are correct.
- All data sent from a get or post request must be processed through a Django Form object.


form_page.html
```html
{% extends 'django_spire/page/form_full_page.html' %}

{% block full_page_content %}
    <div class="row g-3">
        <div class="col-12">
            {% include 'friend/card/form_card.html' %}
        </div>
    </div>
{% endblock %}
```

form_card.html
```html
{% extends 'django_spire/card/title_card.html' %}

{% block card_title %}
    Friend
{% endblock %}

{% block card_title_content %}
    {% include 'friend/form/form.html' %}
{% endblock %}
```

### Important note
- Look at the model of the main object so see what attributes you should add to this item.
- This should include all the model fields that are editable.


form.html
```html
<form
    method="POST"
    x-data="{
        async init() {
            await this.friend.get()
        },
        friend: new ModelObjectGlue('friend')
    }"
>
    {% csrf_token %}

    {% include 'django_spire/element/divider_element.html' with divider_title='Personal Information' %}

    <div class="row g-3 mb-3">
        <div class="col-md-4">
            {% include 'django_glue/form/field/char_field.html' with glue_model_field='friend.first_name' %}
        </div>
        <div class="col-md-4">
            {% include 'django_glue/form/field/char_field.html' with glue_model_field='friend.middle_name' %}
        </div>
        <div class="col-md-4">
            {% include 'django_glue/form/field/char_field.html' with glue_model_field='friend.last_name' %}
        </div>
    </div>

    {% include 'django_spire/element/divider_element.html' with divider_title='Personal Details' %}

    <div class="row g-3 mb-3">
        <div class="col-md-6">
            {% include 'django_glue/form/field/date_field.html' with glue_model_field='friend.birth_date' %}
        </div>
        <div class="col-md-6">
            {% include 'django_glue/form/field/char_field.html' with glue_model_field='friend.favorite_colour' %}
        </div>
    </div>

    {% include 'django_spire/element/divider_element.html' with divider_title='Relationship Information' %}

    <div class="row g-3 mb-3">
        <div class="col-md-6">
            {% include 'django_glue/form/field/select_field.html' with glue_model_field='friend.love_language' %}
        </div>
        <div class="col-md-6">
            {% include 'django_glue/form/field/select_field.html' with glue_model_field='friend.relationship_values' %}
        </div>
    </div>

    <div class="row g-3 mb-3">
        <div class="col-12">
            {% include 'django_glue/form/field/text_field.html' with glue_model_field='friend.favorite_memories' %}
        </div>
    </div>

    <div class="row">
        <div class="col-12">
            {% include 'django_spire/contrib/form/button/form_submit_button.html' %}
        </div>
    </div>

</form>
```