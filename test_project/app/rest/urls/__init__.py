from django.urls import path, include

app_name = 'rest'

urlpatterns = [
    path('page/', include('test_project.app.rest.urls.page_urls'), name='page'),
    path('template/', include('test_project.app.rest.urls.template_urls'), name='template'),
]
