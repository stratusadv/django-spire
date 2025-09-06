from django.urls import path, include


app_name = 'user'

urlpatterns = [
    path('page/', include('django_spire.auth.user.urls.page_urls', namespace='page')),
    path('form/', include('django_spire.auth.user.urls.form_urls', namespace='form')),
]
