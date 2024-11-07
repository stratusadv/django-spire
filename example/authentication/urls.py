from django.urls import path

from example.authentication import views


app_name = 'authentication'

urlpatterns = [
    path('<int:pk>/detail', views.authentication_detail_view, name='detail')
]
