from __future__ import annotations

from django.urls import path

from django_spire.auth.views import redirect_views


app_name = 'redirect'

urlpatterns = [
    path('login/',
         redirect_views.login_redirect_view,
         name='login'),

    path('logout/',
         redirect_views.logout_redirect_view,
         name='logout'),
]
