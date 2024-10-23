from django.urls import path
from django_spire.user_account.authentication.mfa.views import page_views

app_name = 'page'
urlpatterns = [
    path('form/',
         page_views.mfa_form_view,
         name='form'),
]
