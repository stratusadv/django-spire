---
name: list-templates
description: Examples on how we implement our list templates (pages, cards, items). 
---

# Guidelines
- Use the examples as the base implementation. 
- You will have to refactor out friend and ensure the custom paths are correct.
- All django spire paths are correct.


list_page.html
```html
{% extends 'django_spire/page/full_page.html' %}

{% block full_page_content %}
    <div class="row">
        <div class="col-12">
            {% include 'friend/card/list_card.html' %}
        </div>
    </div>
{% endblock %}
```

list_card.html
```html
{% extends 'django_spire/card/title_card.html' %}

{% block card_title %}
    Friends
{% endblock %}

{% block card_button %}
    {% if perms.friend.add_friend %}
        {% url 'mort:friend:form:create' as new_friend_url %}
        {% include 'django_spire/button/primary_dark_button.html' with button_text='Add' button_icon='bi bi-plus' button_href=new_friend_url %}
    {% endif %}
{% endblock %}

{% block card_title_content %}
    {% for friend in friends %}
    	{% include 'friend/item/item.html' %}
    {% empty %}
        {% include 'django_spire/item/no_data_item.html' %}
    {% endfor %}
{% endblock %}
```

### Important note
- Look at the model of the main object so see what attributes you should add to this item.
- It is a high level summary

item.html
```html
{% extends 'django_spire/item/item.html' %}

{% block item_title %}
    {% url 'mort:friend:page:detail' pk=friend.pk as friend_view_url %}
    {% include 'django_spire/element/attribute_element.html' with attribute_title='Friend' attribute_value=friend.first_name attribute_href=friend_view_url %}
{% endblock %}

{% block item_row_content %}
    <div class="col-6">
        {% include 'django_spire/element/attribute_element.html' with attribute_title='Last Name' attribute_value=friend.last_name %}
    </div>
{% endblock %}

{% block item_button %}
    {% url 'mort:friend:page:detail' pk=friend.pk as friend_view_url %}

    {% if perms.friend.change_friend %}
        {% url 'mort:friend:form:update' pk=friend.pk as friend_edit_url %}
    {% endif %}

    {% if perms.friend.delete_friend %}
        {% url 'mort:friend:form:delete' pk=friend.pk as friend_delete_url %}
    {% endif %}

    {% include 'django_spire/dropdown/ellipsis_dropdown.html' with view_url=friend_view_url edit_url=friend_edit_url delete_url=friend_delete_url %}
{% endblock %}
```