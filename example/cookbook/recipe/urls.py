from django.urls import path

from example.cookbook.recipe import views


app_name = 'recipe'

urlpatterns = [
    path('list/', views.recipe_list_view, name='list'),
    path('<int:pk>/detail', views.recipe_detail_view, name='detail'),
    path('<int:pk>/form', views.recipe_form_view, name='form'),
    path('<int:cookbook_pk>/recipe/<int:pk>/form', views.recipe_form_view, name='cookbook_form'),
    path('<int:pk>/delete/form', views.recipe_detail_view, name='delete'),
]
