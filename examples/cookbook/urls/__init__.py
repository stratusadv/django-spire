from django.urls import path, include


app_name = '__init__'

urlpatterns = [
    path('', include('examples.cookbook.urls.page_urls', namespace='page')),
    path('recipe/', include('examples.cookbook.recipe.urls', namespace='recipe')),
]
