from django.urls import path, include


app_name = '__init__'

urlpatterns = [
    path('', include('examples.cookbook.recipe.urls.page_urls', namespace='page')),
    path('nutrition/', include('examples.cookbook.recipe.nutrition.urls', namespace='nutrition')),
]
