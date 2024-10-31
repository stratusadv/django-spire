from django.urls import path

from django_spire.authentication.views import redirect_views


app_name = 'authentication'

urlpatterns = [
    path('login/redirect/',
         redirect_views.login_redirect_view,
         name='login'),

    path('logout/redirect/',
         redirect_views.logout_redirect_view,
         name='logout'),
]
