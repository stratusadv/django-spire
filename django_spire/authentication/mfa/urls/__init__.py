from django.urls import include, path


app_name = '__init__'

urlpatterns  = [
    path('', include('django_spire.authentication.mfa.urls.page_urls', namespace='page')),
    path('', include('django_spire.authentication.mfa.urls.redirect_urls', namespace='redirect')),
]
