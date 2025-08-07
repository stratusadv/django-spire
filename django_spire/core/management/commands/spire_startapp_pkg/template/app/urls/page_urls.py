from django.urls import path

from module.views import page_views

app_name = 'page'
urlpatterns = [
    path('<int:pk>/detail/', page_views.spireparentapp_spirechildapp_detail_view, name='detail'),
    path('list/', page_views.spireparentapp_spirechildapp_list_view, name='list'),
]