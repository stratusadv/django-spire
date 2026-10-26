from django.urls import path

from test_project.app.metrics import views

app_name = 'page'

urlpatterns = [
    path('record_test/', views.record_test_page_view, name='record_test'),
    path('record_click/', views.record_click_view, name='record_click'),
]
