from django.urls import path, include


app_name = 'authentication'

urlpatterns = [
    path('', include('django_spire.authentication.urls.admin_urls', namespace='admin')),
    path('redirect/', include('django_spire.authentication.urls.redirect_urls', namespace='redirect')),
    path('mfa/', include('django_spire.authentication.mfa.urls', namespace='mfa')),
]
