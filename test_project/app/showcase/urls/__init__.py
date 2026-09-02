from django.urls import include, path

app_name = 'showcase'

urlpatterns = [
    path('page/', include('test_project.app.showcase.urls.page_urls', namespace='page')),
]
