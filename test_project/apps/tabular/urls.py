from django.urls import path
from test_project.apps.tabular import views

app_name = 'tabular'

urlpatterns = [
    path('', views.tabular_home_view, name='home'),
    path('api/rows/', views.tabular_rows_view, name='rows'),
    path('api/<int:task_id>/children/', views.tabular_child_rows_view, name='child_rows'),
]
