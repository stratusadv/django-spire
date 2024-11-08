from django.urls import include, path

from example.authentication import views


app_name = 'authentication'

urlpatterns = [
    path('', views.authentication_home_view, name='home'),
    path('list/', views.authentication_list_view, name='list'),
    path('<int:pk>/detail/', views.authentication_detail_view, name='detail')
]


urlpatterns += [
    path('mfa/', include('example.authentication.mfa.urls', namespace='mfa')),
]
