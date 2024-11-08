from django.urls import include, path

from example.user_account import views


app_name = 'user_account'

urlpatterns = [
    path('', views.user_account_home_view, name='home'),
    path('list/', views.user_account_list_view, name='list'),
    path('<int:pk>/detail/', views.user_account_detail_view, name='detail')
]

urlpatterns += [
    path('profile/', include('example.user_account.profile.urls', namespace='profile')),
]
