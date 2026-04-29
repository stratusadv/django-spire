from django.urls import path, include

app_name = 'rest'

urlpatterns = [
    path('page/', include('test_project.apps.rest.urls.page_urls'), name='page'),
    path('template/', include('test_project.apps.rest.urls.template_urls'), name='template'),
]
