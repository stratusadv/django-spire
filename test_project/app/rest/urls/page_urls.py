from django.contrib.auth.decorators import login_required
from django.urls import path

from test_project.app.rest.components import PirateTableComponent
from test_project.app.rest.views import page_views

app_name = 'page'

urlpatterns = [
    path('list/', page_views.list_page, name='list'),
    path('detail/<int:pk>/', page_views.detail_page, name='detail'),
    path('table/', login_required(PirateTableComponent.as_view()), name='table'),
]
