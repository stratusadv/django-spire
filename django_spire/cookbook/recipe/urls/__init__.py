from django.urls import path, include

app_name = '__init__'
urlpatterns = [
    path('', include('app.cookbook.recipe.urls.page_urls', namespace='page')),
    path('nutrition/', include('app.cookbook.recipe.nutrition.urls', namespace='nutrition')),
]