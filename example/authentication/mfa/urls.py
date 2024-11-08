from django.urls import path

from example.authentication.mfa import views


app_name = 'authentication_mfa'

urlpatterns = [
    path('', views.authentication_mfa_list_view, name='list'),
    path('<int:pk>/detail', views.authentication_mfa_detail_view, name='detail'),
]
