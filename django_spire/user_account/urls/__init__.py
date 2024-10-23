from django.urls import path, include

app_name = '__init__'
urlpatterns = [
    path("authentication/", include('app.user_account.authentication.urls', namespace='authentication')),
    path('profile/', include('app.user_account.profile.urls', namespace='profile')),
]
