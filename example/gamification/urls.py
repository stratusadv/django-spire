from django.urls import path

from example.gamification import views


app_name = 'gamification'

urlpatterns = [
    path('', views.gamification_home_view, name='home'),
    path('list/', views.gamification_list_view, name='list'),
    path('<int:pk>/detail/', views.gamification_detail_view, name='detail')
]
