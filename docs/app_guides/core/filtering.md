Learn the process of searching and filtering on a list page using Django Spire and Django Glue.

!!! warning
    This tutorial does not go into the details of Django Glue. A basic understanding of [Django Glue](https://django-glue.stratusadv.com/) is recommended before starting this guide.

### Step 1: Create a `ListFilter` instance in the backend.

```python title='app/person/views.py'
from django_spire.core.filtering.list_filters import ListFilter

def person_list_view(request):
    list_filter = ListFilter(request, 'person_list_filter')
```

!!! note "Default Filtering Options"
    Use the `default_filtering_data` parameter to set the default filtering options.

    ```python title='app/person/views.py'
    from django_spire.core.filtering.list_filters import ListFilter, FilterData
    
    def person_list_view(request):
        list_filter = ListFilter(
            request,
            'person_list_filter',
            default_filtering_data=FilterData({'age': 25})
        )
    ```

### Step 2: Override the following methods in the objects QuerySet class.

#### For Filtering:
Override the `filter_by_query_dict` method in the objects QuerySet class.

```python title='app/person/querysets.py'
from django.db.models import Q, QuerySet

class PersonQuerySet(QuerySet):
    def filter_by_query_dict(self, filter_data: dict) -> QuerySet:
        query = Q()
        
        age = filter_data.get('age')
        if age:
            query &= Q(age=age)

        return self.filter(query)
```


#### For Searching: 
Override the `search` method in the objects QuerySet class.

```python title='app/person/querysets.py'
from django.db.models import Q, QuerySet

class PersonQuerySet(QuerySet):
    def search(self, search_query: str) -> QuerySet:
        return self.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
```


### Step 3: Query for the objects using the `ListFilter` instance.

The filtering / searching will be handled inside the `process_queryset` method using the methods that were just overridden.

```python title='app/person/views.py'
from app.person.models import Person
from django_spire.core.filtering.list_filters import ListFilter

def person_list_view(request):
    list_filter = ListFilter(request, 'person_list_filter')

    people = list_filter.process_queryset(Person.objects.all())
```


### Step 4: Pass the `ListFilter` instance and objects to the template.

```python title='app/person/views.py'
from app.person.models import Person
from django_spire.core.filtering.list_filters import ListFilter

def person_list_view(request):
    list_filter = ListFilter(request, 'person_list_filter')

    people = list_filter.process_queryset(Person.objects.all())

    return TemplateResponse(
        request,
        'person/page/list_page.html',
        {
            'people': people,
            'list_filter': list_filter
        }
    )
```


### Step 5: Create a Django Glue form that extends a filter html file. 

Include the form file in your template. For this example, only the Django Glue form will be shown.

#### Only Searching

``` title='person/form/search_form.html'
{% extends 'django_spire/filtering/search_filter.html' %}

{% block filter_key %}{{ list_filter.filter_key }}{% endblock %}

{% block filter_content %}
    <div
        class="row"
        x-data="{
            init() {
                this.search_value.set_attribute('placeholder', 'Search first and last name...')
            },
            search_value: new GlueCharField(
                'search_value',
                {
                    value: '{{ list_filter.filter_data.search_value }}',
                    label: 'Search',
                    name: 'search_value',
                }
            )
        }"
    >
        <div class="col-12">
        </div>
    </div>
{% endblock %}
```

[//]: # (Insert into form when not breaking build, Add {% %}) 
 include 'django_glue/form/field/char_field.html' with glue_field='search_value'


#### Filtering (Searching can be included)

``` title='person/form/filter_form.html'
{% extends 'django_spire/filtering/list_filter.html' %}

{% block filter_key %}{{ list_filter.filter_key }}{% endblock %}

{% block filter_content %}
    <div
        class="row"
        x-data="{
            init() {
                this.search_value.set_attribute('placeholder', 'Search first and last name...')
            },
            age: new GlueIntegerField(
                'age',
                {
                    value: {{ list_filter.filter_data.age|default:'null' }},
                }
            ),
            search_value: new GlueCharField(
                'search_value',
                {
                    value: '{{ list_filter.filter_data.search_value }}',
                    label: 'Search',
                    name: 'search_value',
                }
            )
        }"
    >
        <div class="col-12">
        </div>
        <div class="col-12">
        </div>
    </div>
{% endblock %}
```

[//]: # (Insert into form when not breaking build, Add {% %}) 
 include 'django_glue/form/field/char_field.html' with glue_field='search_value'
 include 'django_glue/form/field/number_field.html' with glue_field='age

### More Complex Example
```python title='app/person/views.py'
from app.person.models import Person
from app.person.choices import PersonHairColourChoices
from django_spire.core.filtering.list_filters import ListFilter, FilterData

def person_list_view(request):
    list_filter = ListFilter(
        request,
        'person_list_filter',
        default_filtering_data=FilterData(
            {
                'age': '25',
                'hair_colour_choices': [
                    PersonHairColourChoices.BLACK,
                    PersonHairColourChoices.BROWN
                ],
            }            
        }
    )

    people = list_filter.process_queryset(Person.objects.all())

    return TemplateResponse(
        request,
        'person/page/list_page.html',
        {
            'people': people,
            'list_filter': list_filter,
            'hair_colour_choices': [
                [choice.value, choice.label] for choice in PersonHairColourChoices.choices
            ]
        }
    )
```

```python title='app/person/querysets.py'
import json
from django.db.models import Q, QuerySet

class PersonQuerySet(QuerySet):
    def filter_by_query_dict(self, filter_data: dict) -> QuerySet:
        query = Q()

        age = filter_data.get('age')
        if age:
            query &= Q(age=age)
            
        no_selected_choices = [None, 'false', '']
        
        hair_colour_choices = filter_data.get('hair_colour_choices')
        if hair_colour_choices not in no_selected_choices:
            if isinstance(hair_colour_choices, str):
                hair_colour_choices = json.loads(hair_colour_choices)
            if hair_colour_choices:
                query &= Q(status__in=hair_colour_choices)

        return self.filter(query).distinct().order_by('first_name', 'last_name')
```

``` title='person/form/filter_form.html'
{% extends 'django_spire/filtering/list_filter.html' %}

{% block filter_key %}{{ list_filter.filter_key }}{% endblock %}

{% block filter_content %}
    <div
        class="row"
        x-data="{
            init() {
                this.search_value.set_attribute('placeholder', 'Search first and last name...')
            },
            age: new GlueIntegerField(
                'age',
                {
                    value: {{ list_filter.filter_data.age|default:0 }},
                }
            ),
            search_value: new GlueCharField(
                'search_value',
                {
                    value: '{{ list_filter.filter_data.search_value }}',
                    label: 'Search',
                    name: 'search_value',
                }
            ),
            'hair_colour_choices': new GlueIntegerField(
                'hair_colour_choices',
                {
                    value: {{ list_filter.filter_data.hair_colour_choices|default:'null' }},
                    choices: {{ hair_colour_choices }},
                }
            ),
        }"
    >
        <div class="col-12">
        </div>
        <div class="col-12">
        </div>
        <div class="col-12">
        </div>
    </div>
{% endblock %}
```

[//]: # (Insert into form when not breaking build, Add {% %}) 
 include 'django_glue/form/field/char_field.html' with glue_field='search_value'
 include 'django_glue/form/field/number_field.html' with glue_field='age'
 include 'django_glue/form/field/multi_select_field.html' with glue_field='hair_colour_choices'
