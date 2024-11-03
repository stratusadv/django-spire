from django.urls import path

from django_spire.user_account.views import page_views


app_name = 'user_account'

urlpatterns = [
    path('register/user/',
         page_views.register_user_form_view,
         name='register_user_form'
     )
]
