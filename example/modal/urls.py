from django.urls import path

from example.modal import views


app_name = 'modal'

urlpatterns = [
    path('', views.modal_home_view, name='home'),
    path('detail/', views.modal_detail_view, name='detail'),
    path('basic/', views.modal_basic, name='modal_basic'),
    path('page1/', views.modal_page_one, name='modal_page_one'),
    path('page2/', views.modal_page_two, name='modal_page_two'),
    path('page3/', views.modal_page_three, name='modal_page_three'),
    path('submit/', views.modal_form_submit, name='modal_form_submit'),
]
