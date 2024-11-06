from django.urls import path

from examples.user_account import views


app_name = 'user_account'

urlpatterns = [
    path('<int:pk>/detail', views.user_account_detail_view, name='detail')
]
