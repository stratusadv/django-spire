The report app is designed to provide a simple and flexible way to create printable reports within Django Spire applications.

Key features include:
- Easy report class for creation and customization.
- Support for dynamic data sources and filters.
- Integration with Django Spire's authentication and authorization system.

## Installation

Simple add the `django_spire.metric.report` application to your `INSTALLED_APPS` and the `DJANGO_SPIRE_REPORT_REGISTRIES` to your settings:

```python title="settings.py"
INSTALLED_APPS = [
    ...
    'django_spire.metric.report',
    ...
]

# this will be a list of ReportRegistry class module paths to be loaded
DJANGO_SPIRE_REPORT_REGISTRIES = []
```

You also need to add django spire to your projects `urls.py`:

```python title="urls.py"
from django.urls import path, include

urlpatterns = [
    path('django_spire/', include('django_spire.urls', namespace='django_spire')),
]
```

## Usage

Create a link to the report app in your project's navigation or menu using the url `django_spire:metric:report:page:report`.

Next create the report you want to generate. 
This can be done by defining a report class that inherits from `django_spire.metric.report.report.BaseReport` and implementing the necessary methods for data retrieval and report generation.

Example:

```python title="test_project/apps/queryset_filtering/reports/task_counting_monthly_report.py"

--8<-- "test_project/apps/queryset_filtering/reports/task_counting_monthly_report.py"

```

After we complete our report we want to create a registry so all reports in this app are together

Example:

```python title="test_project/apps/queryset_filtering/reports/task_report_registry.py"

--8<-- "test_project/apps/queryset_filtering/reports/task_report_registry.py"

```

The final step is to add the registry to our settings file so it automatically adds to the page view.

```python title="settings.py"

# Report Registry
DJANGO_SPIRE_REPORT_REGISTRIES = [
    'test_project.apps.queryset_filtering.reports.task_report_registry.TaskReportRegistry'
]

```

All done, we will now see our report in the sub navigation of the report app and be able to print.