from django.urls import path

from example.user_account.profile import views


app_name = 'profile'

urlpatterns = [
    path('<int:pk>/detail', views.profile_detail_view, name='detail')
]
