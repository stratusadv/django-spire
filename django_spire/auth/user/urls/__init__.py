from django.urls import path, include


app_name = 'user'

urlpatterns = [
    path('', include('django_spire.auth.user.urls.page_urls', namespace='page')),
]
