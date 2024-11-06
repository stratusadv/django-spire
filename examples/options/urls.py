from django.urls import path

from examples.options import views


app_name = 'options'

urlpatterns = [
    path('<int:pk>/detail', views.options_detail_view, name='detail')
]
