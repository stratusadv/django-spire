from django.urls import path

from example.user_account.profile import views


app_name = 'profile'

urlpatterns = [
    path('', views.profile_home_view, name='home'),
    path('list/', views.profile_list_view, name='list'),
    path('<int:pk>/detail/', views.profile_detail_view, name='detail')
]
