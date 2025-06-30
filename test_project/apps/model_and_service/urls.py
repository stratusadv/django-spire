from django.urls import path

from test_project.apps.model_and_service import views

app_name = 'test_model'

urlpatterns = [
    path('', views.test_model_home_view, name='home'),
    path('list/', views.test_model_list_view, name='list'),
    path('detail/', views.test_model_detail_view, name='detail')
]
