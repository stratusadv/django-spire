from django.urls import include, path


app_name = '__init__'

urlpatterns = [
    path("authentication/", include('django_spire.authentication.urls', namespace='authentication')),
    path('profile/', include('django_spire.user_account.profile.urls', namespace='profile')),
]
