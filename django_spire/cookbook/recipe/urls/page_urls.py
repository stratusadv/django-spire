from django.urls import path, include
from django_spire.cookbook.recipe.views import page_views

app_name = 'recipe'
urlpatterns = [
    path('list/', page_views.recipe_list_view, name='list'),
    path('<int:pk>/detail', page_views.recipe_detail_view, name='detail'),
    path('<int:pk>/form', page_views.recipe_form_view, name='form'),
    path('<int:cookbook_pk>/recipe/<int:pk>/form', page_views.recipe_form_view, name='cookbook_form'),
    path('<int:pk>/delete/form', page_views.recipe_detail_view, name='delete'),
]
