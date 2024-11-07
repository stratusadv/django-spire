from django.urls import path

from example.breadcrumb import views


app_name = 'breadcrumb'

urlpatterns = [
    path('<int:pk>/detail', views.breadcrumb_detail_view, name='detail')
]
