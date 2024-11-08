from django.urls import path

from example.options import views


app_name = 'options'

urlpatterns = [
    path('', views.options_list_view, name='list'),
    path('<int:pk>/detail', views.options_detail_view, name='detail')
]
