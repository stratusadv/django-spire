from django.urls import path, include


app_name = '__init__'

urlpatterns = [
    path('', include('django_spire.authentication.urls.admin_urls', namespace='admin')),
    path('', include('django_spire.authentication.urls.redirect_urls', namespace='redirect')),
    path('mfa/', include('django_spire.authentication.mfa.urls', namespace='mfa')),
]
