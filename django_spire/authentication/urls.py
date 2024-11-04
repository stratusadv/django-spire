from django.urls import include, path


app_name = 'authentication'

urlpatterns = [
    path('admin/', include('django_spire.authentication.admin_urls')),
    path('redirect/', include('django_spire.authentication.redirect_urls')),
]
