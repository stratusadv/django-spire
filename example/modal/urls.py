from django.urls import path

from example.modal import views


app_name = 'modal'

urlpatterns = [
    path('', views.modal_page_view, name='home'),
    path('page1/', views.modal_page_one, name='modal_page_one'),
    path('page2/', views.modal_page_two, name='modal_page_two'),
    path('page3/', views.modal_page_three, name='modal_page_three'),
    path('submit/', views.modal_form_submit, name='modal_form_submit'),
]
