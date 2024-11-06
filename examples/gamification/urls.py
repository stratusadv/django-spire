from django.urls import path

from examples.gamification import views


app_name = 'gamification'

urlpatterns = [
    path('<int:pk>/detail', views.gamification_detail_view, name='detail')
]
