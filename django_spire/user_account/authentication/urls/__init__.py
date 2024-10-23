from django.urls import path, include


app_name = '__init__'
urlpatterns = [
    path('', include('app.user_account.authentication.urls.admin_urls', namespace='admin')),
    path('', include('app.user_account.authentication.urls.redirect_urls', namespace='redirect')),
    path('mfa/', include('app.user_account.authentication.mfa.urls', namespace='mfa')),
]