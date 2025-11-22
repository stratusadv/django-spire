from django.urls import include, path

app_name = 'tabular'

urlpatterns = [
    path('form/', include('test_project.apps.tabular.urls.form_urls', namespace='form')),
    path('page/', include('test_project.apps.tabular.urls.page_urls', namespace='page')),
    path('template/', include('test_project.apps.tabular.urls.template_urls', namespace='template'))
]
