from django.urls import path

from examples.help import views


app_name = 'help'

urlpatterns = [
    path('<int:pk>/detail', views.help_detail_view, name='detail')
]
