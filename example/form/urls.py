from django.urls import path

from example.form import views


app_name = 'form'

urlpatterns = [
    path('', views.form_list_view, name='list'),
    path('<int:pk>/detail', views.form_detail_view, name='detail')
]
