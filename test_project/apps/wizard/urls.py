from django.urls import path

from test_project.apps.wizard import views


app_name = 'wizard'

urlpatterns = [
    path('', views.wizard_home_view, name='home'),
    path('detail/', views.wizard_detail_view, name='detail'),
    path('page1/', views.wizard_page_one, name='wizard_page_one'),
    path('page2/', views.wizard_page_two, name='wizard_page_two'),
    path('page3/', views.wizard_page_three, name='wizard_page_three'),
    path('submit/', views.wizard_form_submit, name='wizard_form_submit'),
]
