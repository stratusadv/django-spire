---
name: detail-templates
description: Examples on how we implement our detail templates (page and card). 
---

# Guidelines
- Use the examples as the base implementation. 
- You will have to refactor out friend and ensure the custom paths are correct.
- All django spire paths are correct.


# Examples

### Important note
- In col-md-8 we can add as many related objects here. They can be detail cards or list cards.


details_page.html
```html
{% extends 'django_spire/page/full_page.html' %}

{% block full_page_content %}
    <div class="row g-3">
        <div class="col-12">
            {% include 'friend/card/detail_card.html' %}
        </div>
        
        <div class="col-md-8">
            {% include 'friend/chin_waggle/card/list_card.html' %}
        </div>
        <div class="col-md-4">
            {% include 'django_spire/activity/card/list_card.html' with activity_log=friend.activity_log.prefetch_user %}
        </div>
    </div>
{% endblock %}

```

### Important note
- Look at the model of the main object so see what attributes you should add to this item.
- It is a detailed summary.
- Add dividers and group information where needed.

detail_card.html
```html
{% extends 'django_spire/card/title_card.html' %}

{% block card_title %}
    Friend
{% endblock %}

{% block card_button %}
    {% if perms.friend.change_friend %}
        {% url 'mort:friend:form:update' pk=friend.pk as friend_edit_url %}
        {% include 'django_spire/button/primary_dark_button.html' with button_text='Edit' button_icon='bi bi-pencil' button_href=friend_edit_url %}
    {% endif %}
{% endblock %}

{% block card_title_content %}
    <div class="row g-3">
        <div class="col-12">
            {% include 'django_spire/element/attribute_element.html' with attribute_title='Name' attribute_value=friend.first_name %}
        </div>

        <div class="col-12">
            {% include 'django_spire/element/attribute_element.html' with attribute_title='Description' attribute_value=friend.last_name %}
        </div>
    </div>
{% endblock %}

```