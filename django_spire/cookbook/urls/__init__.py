from django.urls import path, include


app_name = '__init__'
urlpatterns = [
    path('', include('app.cookbook.urls.page_urls', namespace='page')),
    path('recipe/', include('app.cookbook.recipe.urls', namespace='recipe')),
]
