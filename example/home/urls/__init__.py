from django.urls import path, include

app_name = 'home'

urlpatterns = [
    path('', include('example.home.urls.page_urls', namespace='page')),
]
