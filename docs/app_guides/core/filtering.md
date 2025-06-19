Learn the process of searching and filtering on a list page using Django Spire and Django Glue.

!!! warning
    This tutorial does not go into the details of Django Glue. A basic understanding of [Django Glue](https://django-glue.stratusadv.com/) is recommended before starting this guide.

### Step 1: Create a `QuerySetFilter` instance in the backend.

```python title='app/person/views.py'
from django_spire.core.filtering.filters import QuerySetFilter


def person_list_view(request):
    queryset_filter = QuerySetFilter(request, filter_key='person_queryset_filter')
```

!!! note "Default Filtering Options"
    Use the `default_filtering_data` parameter to set the default filtering options.

    ```python title='app/person/views.py'
    from django_spire.core.filtering.filters import QuerySetFilter
    
    def person_list_view(request):
        queryset_filter = QuerySetFilter(
            request,
            filter_key='person_queryset_filter',
            default_filtering_data={'age': 25}
        )
    ```

### Step 2: Inherit from `FilterQuerySet` or `SearchQuerySet` in the objects QuerySet class and override the abstract method.

#### For Filtering:
Inherit from `FilterQuerySet` and override the `filter_by_query_dict` method in the objects QuerySet class.

```python title='app/person/querysets.py'
from django.db.models import Q, QuerySet
from django_spire.core.filtering.querysets import FilterQuerySet


class PersonQuerySet(FilterQuerySet):
    def filter_by_query_dict(self, filter_data: dict) -> QuerySet:
        query = Q()

        age = filter_data.get('age')
        if age:
            query &= Q(age=age)

        return self.filter(query)
```

#### For Searching: 
Inherit from `SearchQuerySet` and override the `search` method in the objects QuerySet class.

```python title='app/person/querysets.py'
from django.db.models import Q, QuerySet
from django_spire.core.filtering.querysets import SearchQuerySet

class PersonQuerySet(SearchQuerySet):
    def search(self, search_query: str) -> QuerySet:
        return self.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
```


### Step 3: Query for the objects using the `QuerySetFilter` instance.

The filtering / searching will be handled inside the `process_queryset` method using the methods that were just overridden.

```python title='app/person/views.py'
from app.person.models import Person
from django_spire.core.filtering.filters import QuerySetFilter


def person_list_view(request):
    queryset_filter = QuerySetFilter(request, filter_key='person_queryset_filter')

    people = queryset_filter.process_queryset(Person.objects.all())
```


### Step 4: Pass the `QuerySetFilter` instance to the template.

```python title='app/person/views.py'
from app.person.models import Person
from django_spire.core.filtering.filters import QuerySetFilter


def person_list_view(request):
    queryset_filter = QuerySetFilter(request, filter_key='person_queryset_filter')

    people = queryset_filter.process_queryset(Person.objects.all())

    return TemplateResponse(
        request,
        'person/page/list_page.html',
        {
            'people': people,
            'queryset_filter': queryset_filter
        }
    )
```


### Step 5: Create a Django Glue form that extends one of the filter form html files.

#### Filtering
Searching can be included with filtering, see [More Complex Example](#more-complex-example) for an example.

```html title='person/form/filter_form.html'
{% extends 'django_spire/filtering/form/filter_form.html' %}

{% block filter_key %}{{ queryset_filter.filter_key }}{% endblock %}

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
                    value: {{ queryset_filter.filter_data.age|default:'null' }},
                }
            )
        }"
    >
        Include block tags {% %} excluded due to mkdocs attempting to render file.
        <div class="col-12">
            include 'django_glue/form/field/number_field.html' with glue_field='age'
        </div>
    </div>
{% endblock %}
```

#### Searching

```html title='person/form/search_form.html'
{% extends 'django_spire/filtering/form/search_form.html' %}

{% block filter_key %}{{ queryset_filter.filter_key }}{% endblock %}

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
                    value: '{{ queryset_filter.filter_data.search_value }}',
                    label: 'Search',
                    name: 'search_value',
                }
            )
        }"
    >
        Include block tags {% %} excluded due to mkdocs attempting to render file.
        <div class="col-12">
            include 'django_glue/form/field/char_field.html' with glue_field='search_value'
        </div>
    </div>
{% endblock %}
```

### More Complex Example

```python title='app/person/views.py'
from app.person.models import Person
from app.person.choices import PersonHairColourChoices
from django_spire.core.filtering.filters import QuerySetFilter


def person_list_view(request):
    queryset_filter = QuerySetFilter(
        request,
        filter_key='person_queryset_filter',
        default_filtering_data={
            'age': '25',
            'hair_colour_choices': [
                PersonHairColourChoices.BLACK,
                PersonHairColourChoices.BROWN
            ],
        }
    )

    people = queryset_filter.process_queryset(Person.objects.all())

    return TemplateResponse(
        request,
        'person/page/list_page.html',
        {
            'people': people,
            'queryset_filter': queryset_filter,
            'hair_colour_options': [
                [choice.value, choice.label]
                for choice in PersonHairColourChoices.choices
            ]
        }
    )
```

```python title='app/person/querysets.py'
import json
from django.db.models import Q, QuerySet
from django_spire.core.filtering.querysets import FilterQuerySet, SearchQuerySet


class PersonQuerySet(FilterQuerySet, SearchQuerySet):
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

    def search(self, search_query: str) -> QuerySet:
        return self.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
```

```html title='person/form/filter_form.html'
{% extends 'django_spire/filtering/form/filter_form.html' %}

{% block filter_key %}{{ queryset_filter.filter_key }}{% endblock %}

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
                    value: {{ queryset_filter.filter_data.age|default:0 }},
                }
            ),
            search_value: new GlueCharField(
                'search_value',
                {
                    value: '{{ queryset_filter.filter_data.search_value }}',
                    label: 'Search',
                    name: 'search_value',
                }
            ),
            'hair_colour_choices': new GlueIntegerField(
                'hair_colour_choices',
                {
                    value: {{ queryset_filter.filter_data.hair_colour_choices|default:'null' }},
                    choices: {{ hair_colour_options }},
                }
            ),
        }"
    >
        Include block tags {% %} excluded due to mkdocs attempting to render file.
        <div class="col-12">
            include 'django_glue/form/field/char_field.html' with glue_field='search_value'
        </div>
        <div class="col-12">
            include 'django_glue/form/field/number_field.html' with glue_field='age'
        </div>
        <div class="col-12">
            include 'django_glue/form/field/multi_select_field.html' with glue_field='hair_colour_choices'
        </div>
    </div>
{% endblock %}
```
