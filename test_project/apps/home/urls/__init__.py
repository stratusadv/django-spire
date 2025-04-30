from django.urls import path, include

app_name = 'home'

urlpatterns = [
    path('', include('test_project.apps.home.urls.page_urls', namespace='page')),
]
