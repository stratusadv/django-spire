from django.urls import path

from django_spire.core.search.views import search_palette_view, search_results_view


app_name = 'search'

urlpatterns = [
    path('search-palette/', search_palette_view, name='search_palette'),
    path('results/', search_results_view, name='results'),
]
