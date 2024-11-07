from django.urls import path

from example.authentication.mfa import views


app_name = 'authentication_mfa'

urlpatterns = [
    path('<int:pk>/detail', views.authentication_mfa_detail_view, name='detail'),
]
