from django.urls import path

from test_project.apps.infinite_scrolling.views import page_views


app_name = 'page'

urlpatterns = [
    path('cards/', page_views.cards_page_view, name='cards'),
    path('list/', page_views.list_page_view, name='list'),
    path('table/', page_views.table_page_view, name='table'),
    path('<int:pk>/detail/', page_views.detail_page_view, name='detail'),
    path('<int:pk>/delete/', page_views.delete_page_view, name='delete'),
]
