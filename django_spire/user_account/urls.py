from django.urls import path, include
from django_spire.user_account.views import page_views

app_name = 'user_account'

urlpatterns = [
    path("register/user/",
         page_views.register_user_form_view,
         name='register_user_form'
     ),
]

urlpatterns += [
    path("authentication/", include('app.user_account.authentication.urls', namespace='authentication')),
    path("profile/", include('app.user_account.profile.urls', namespace='profile')),
]
